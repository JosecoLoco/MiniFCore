from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

class SugerenciasFlow:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['3Dfinal']
            
            # Actualizar los umbrales de stock
            self.STOCK_BAJO = 5    # Stock crítico/bajo: menos de 5 unidades
            self.STOCK_MEDIO = 10  # Stock medio: entre 5 y 10 unidades
            # Stock alto: más de 10 unidades
            
            # Mantener los colores por mes...
            self.colores_por_mes = {
                1: {  # Enero
                    'colores': ['Blanco', 'Dorado', 'Azul'],
                    'eventos': ['Año Nuevo', 'Reyes Magos']
                },
                2: {  # Febrero
                    'colores': ['Rojo', 'Rosa', 'Blanco'],
                    'eventos': ['San Valentín', 'Carnaval']
                },
                3: {  # Marzo
                    'colores': ['Verde', 'Dorado', 'Blanco'],
                    'eventos': ['San Patricio', 'Primavera']
                },
                4: {  # Abril
                    'colores': ['Morado', 'Amarillo', 'Blanco'],
                    'eventos': ['Semana Santa', 'Pascua']
                },
                5: {  # Mayo
                    'colores': ['Rosa', 'Blanco', 'Rojo'],
                    'eventos': ['Día de la Madre', 'Cinco de Mayo']
                },
                6: {  # Junio
                    'colores': ['Azul', 'Rojo', 'Amarillo'],
                    'eventos': ['Día del Padre', 'Verano']
                },
                7: {  # Julio
                    'colores': ['Rojo', 'Azul', 'Blanco'],
                    'eventos': ['Fiestas Patrias', 'Verano']
                },
                8: {  # Agosto
                    'colores': ['Verde', 'Blanco', 'Rojo'],
                    'eventos': ['Verano', 'Fiestas Locales']
                },
                9: {  # Septiembre
                    'colores': ['Verde', 'Blanco', 'Rojo'],
                    'eventos': ['Fiestas Patrias', 'Independencia']
                },
                10: {  # Octubre
                    'colores': ['Naranja', 'Negro', 'Morado'],
                    'eventos': ['Halloween', 'Día de Muertos']
                },
                11: {  # Noviembre
                    'colores': ['Negro', 'Morado', 'Dorado'],
                    'eventos': ['Día de Muertos', 'Buen Fin']
                },
                12: {  # Diciembre
                    'colores': ['Rojo', 'Verde', 'Dorado'],
                    'eventos': ['Navidad', 'Año Nuevo']
                }
            }
            
        except Exception as e:
            print(f"Error al conectar con MongoDB: {e}")
            raise e

    def analizar_tendencias_pedidos(self):
        """
        Analiza las tendencias de pedidos por mes
        """
        try:
            # Obtener todos los pedidos
            pedidos = list(self.db.pedidos.find())
            pedidos_por_mes = {}
            mes_actual = datetime.now().month
            
            # Agrupar pedidos por mes
            for pedido in pedidos:
                fecha_entrega = pedido.get('fecha_entrega')
                if isinstance(fecha_entrega, str):
                    fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d')
                
                if fecha_entrega:
                    mes = fecha_entrega.month
                    if mes not in pedidos_por_mes:
                        pedidos_por_mes[mes] = []
                    pedidos_por_mes[mes].append(pedido)
            
            # Analizar tendencias
            tendencias = {
                'mes_actual': {
                    'mes': mes_actual,
                    'total_pedidos': len(pedidos_por_mes.get(mes_actual, [])),
                    'colores_sugeridos': self.colores_por_mes[mes_actual]['colores'],
                    'eventos': self.colores_por_mes[mes_actual]['eventos']
                },
                'mes_siguiente': {
                    'mes': (mes_actual % 12) + 1,
                    'colores_sugeridos': self.colores_por_mes[(mes_actual % 12) + 1]['colores'],
                    'eventos': self.colores_por_mes[(mes_actual % 12) + 1]['eventos']
                },
                'meses_mas_pedidos': []
            }
            
            # Encontrar los meses con más pedidos
            for mes, pedidos_mes in pedidos_por_mes.items():
                tendencias['meses_mas_pedidos'].append({
                    'mes': mes,
                    'total_pedidos': len(pedidos_mes),
                    'colores_sugeridos': self.colores_por_mes[mes]['colores'],
                    'eventos': self.colores_por_mes[mes]['eventos']
                })
            
            # Ordenar por cantidad de pedidos
            tendencias['meses_mas_pedidos'].sort(key=lambda x: x['total_pedidos'], reverse=True)
            
            return tendencias
            
        except Exception as e:
            print(f"Error al analizar tendencias de pedidos: {e}")
            return None

    def analizar_necesidades_pedidos(self):
        """
        Analiza los pedidos pendientes y en proceso para calcular
        la cantidad de filamentos necesarios (relación 1:1)
        """
        try:
            # Obtener pedidos pendientes y en proceso
            pedidos = list(self.db.pedidos.find({
                'estado': {'$in': ['pendiente', 'en_proceso']}
            }).sort('fecha_entrega', 1))

            necesidades_filamentos = {}
            detalles_pedidos = []
            alertas_stock = []

            for pedido in pedidos:
                try:
                    # Obtener el producto asociado al pedido
                    producto = self.db.productos.find_one({
                        '_id': ObjectId(pedido.get('producto_id'))
                    })
                    
                    if not producto:
                        continue

                    pedido_id = str(pedido.get('_id'))
                    cantidad_pedido = int(pedido.get('cantidad', 1))
                    
                    # Verificar stock para cada filamento necesario
                    filamentos_insuficientes = []
                    for filamento_id in producto.get('filamentos', []):
                        filamento = self.db.filamentos.find_one({
                            '_id': ObjectId(filamento_id)
                        })
                        
                        if not filamento:
                            continue

                        stock_actual = int(filamento.get('stock', 0))
                        
                        # Si el stock es insuficiente para la cantidad del pedido
                        if stock_actual < cantidad_pedido:
                            filamentos_insuficientes.append({
                                'nombre': filamento['nombre'],
                                'color': filamento['color'],
                                'stock_actual': stock_actual,
                                'cantidad_necesaria': cantidad_pedido
                            })

                    # Si hay filamentos insuficientes, crear alerta
                    if filamentos_insuficientes:
                        alertas_stock.append({
                            'pedido_id': pedido_id,
                            'producto_nombre': producto['nombre'],
                            'cantidad': cantidad_pedido,
                            'fecha_entrega': pedido.get('fecha_entrega'),
                            'filamentos_insuficientes': filamentos_insuficientes
                        })

                    # Agregar a detalles_pedidos
                    detalles_pedidos.append({
                        'pedido_id': pedido_id,
                        'producto_nombre': producto['nombre'],
                        'cantidad': cantidad_pedido,
                        'fecha_entrega': pedido.get('fecha_entrega'),
                        'estado': pedido.get('estado', 'pendiente'),
                        'tiene_stock_suficiente': len(filamentos_insuficientes) == 0,
                        'filamentos_insuficientes': filamentos_insuficientes
                    })

                except Exception as e:
                    print(f"Error procesando pedido individual: {e}")
                    continue

            return necesidades_filamentos, detalles_pedidos, alertas_stock

        except Exception as e:
            print(f"Error al analizar necesidades de pedidos: {e}")
            return {}, [], []

    def analizar_stock_filamentos(self):
        """
        Analiza el stock actual de filamentos y genera sugerencias
        considerando los pedidos pendientes
        """
        try:
            necesidades_filamentos, detalles_pedidos = self.analizar_necesidades_pedidos()
            filamentos = list(self.db.filamentos.find())
            sugerencias_stock = {
                'stock_bajo': [],
                'stock_medio': [],
                'stock_alto': [],
                'necesidades_inmediatas': []
            }
            
            for filamento in filamentos:
                try:
                    stock_actual = int(filamento.get('stock', 0))
                    filamento_id = str(filamento['_id'])
                    
                    # Obtener necesidades si existen
                    necesidad = necesidades_filamentos.get(filamento_id, {
                        'cantidad_necesaria': 0,
                        'pedidos_relacionados': []
                    })
                    
                    cantidad_necesaria = necesidad.get('cantidad_necesaria', 0)
                    stock_despues_pedidos = stock_actual - cantidad_necesaria
                    
                    info_filamento = {
                        'id': filamento_id,
                        'nombre': filamento.get('nombre', 'Sin nombre'),
                        'color': filamento.get('color', 'Sin color'),
                        'material': filamento.get('material', 'Sin material'),
                        'stock_actual': stock_actual,
                        'cantidad_necesaria': cantidad_necesaria,
                        'stock_restante': stock_despues_pedidos,
                        'pedidos_relacionados': necesidad.get('pedidos_relacionados', [])
                    }

                    # Calcular urgencia basada en stock actual y necesidades
                    if cantidad_necesaria > 0:
                        info_filamento['recomendacion_compra'] = max(
                            self.STOCK_MEDIO - stock_despues_pedidos,
                            cantidad_necesaria
                        )
                        
                        if stock_despues_pedidos < 0:
                            info_filamento['urgencia'] = 'CRÍTICO'
                            info_filamento['sugerencia'] = (
                                f"¡URGENTE! Faltan {abs(stock_despues_pedidos)} unidades "
                                f"de {info_filamento['nombre']} para cubrir los pedidos actuales"
                            )
                            sugerencias_stock['necesidades_inmediatas'].append(info_filamento)
                        elif stock_despues_pedidos < self.STOCK_BAJO:
                            info_filamento['urgencia'] = 'BAJO'
                            info_filamento['sugerencia'] = (
                                f"Stock insuficiente de {info_filamento['nombre']} - "
                                f"Quedarán solo {stock_despues_pedidos} unidades después de los pedidos actuales"
                            )
                            sugerencias_stock['stock_bajo'].append(info_filamento)
                    else:
                        # Clasificación normal si no hay pedidos pendientes
                        if stock_actual < self.STOCK_BAJO:
                            info_filamento['urgencia'] = 'BAJO'
                            info_filamento['sugerencia'] = f"Stock bajo de {info_filamento['nombre']}"
                            sugerencias_stock['stock_bajo'].append(info_filamento)
                        elif stock_actual <= self.STOCK_MEDIO:
                            info_filamento['urgencia'] = 'MEDIO'
                            info_filamento['sugerencia'] = f"Stock medio de {info_filamento['nombre']}"
                            sugerencias_stock['stock_medio'].append(info_filamento)
                        else:
                            info_filamento['urgencia'] = 'ALTO'
                            info_filamento['sugerencia'] = f"Stock suficiente de {info_filamento['nombre']}"
                            sugerencias_stock['stock_alto'].append(info_filamento)

                except Exception as e:
                    print(f"Error procesando filamento {filamento.get('_id')}: {e}")
                    continue
            
            return sugerencias_stock, detalles_pedidos
            
        except Exception as e:
            print(f"Error al analizar stock de filamentos: {e}")
            return {
                'stock_bajo': [],
                'stock_medio': [],
                'stock_alto': [],
                'necesidades_inmediatas': []
            }, []

    def generar_reporte_sugerencias(self):
        """
        Genera un reporte completo de sugerencias
        """
        try:
            necesidades_filamentos, detalles_pedidos, alertas_stock = self.analizar_necesidades_pedidos()
            sugerencias_stock, _ = self.analizar_stock_filamentos()
            tendencias = self.analizar_tendencias_pedidos()
            
            reporte = {
                'fecha_generacion': datetime.now(),
                'tendencias': tendencias,
                'stock': sugerencias_stock,
                'pedidos_pendientes': detalles_pedidos,
                'alertas_stock': alertas_stock,
                'resumen': {
                    'total_pedidos_pendientes': len(detalles_pedidos),
                    'pedidos_sin_stock': len(alertas_stock),
                    'pedidos_con_stock': len(detalles_pedidos) - len(alertas_stock)
                }
            }
            
            return reporte
            
        except Exception as e:
            print(f"Error al generar reporte de sugerencias: {e}")
            return None

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close() 