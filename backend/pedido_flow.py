from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

class PedidoFlow:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['3Dfinal']
            print("Conexión exitosa a MongoDB - Base de datos: 3Dfinal")
        except Exception as e:
            print(f"Error al conectar con MongoDB: {e}")
            raise e

    def obtener_pedidos_por_fecha(self, fecha_entrega):
        """
        Obtiene todos los pedidos para una fecha de entrega específica
        """
        try:
            # Convertir la fecha de string a datetime si es necesario
            if isinstance(fecha_entrega, str):
                fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d')

            # Buscar pedidos para la fecha específica
            pedidos = list(self.db.pedidos.find({
                'fecha_entrega': fecha_entrega,
                'estado': {'$in': ['pendiente', 'en_proceso']}
            }))

            return pedidos
        except Exception as e:
            print(f"Error al obtener pedidos por fecha: {e}")
            return []

    def analizar_stock_filamentos(self, pedidos):
        """
        Analiza el stock de filamentos necesarios para los pedidos
        """
        try:
            # Diccionario para almacenar el total de filamentos necesarios
            filamentos_necesarios = {}
            # Lista para almacenar los productos que necesitan filamentos
            productos_analizados = []

            for pedido in pedidos:
                # Obtener el producto del pedido
                producto = self.db.productos.find_one({'_id': ObjectId(pedido['producto_id'])})
                if not producto:
                    continue

                # Obtener los filamentos del producto
                if 'filamentos' in producto:
                    for filamento_id in producto['filamentos']:
                        filamento = self.db.filamentos.find_one({'_id': filamento_id})
                        if not filamento:
                            continue

                        # Calcular la cantidad necesaria basada en la cantidad del pedido
                        cantidad_necesaria = pedido['cantidad']
                        
                        # Actualizar el diccionario de filamentos necesarios
                        if filamento['_id'] not in filamentos_necesarios:
                            filamentos_necesarios[filamento['_id']] = {
                                'nombre': filamento['nombre'],
                                'stock_actual': filamento['stock'],
                                'cantidad_necesaria': cantidad_necesaria,
                                'productos': [{
                                    'producto_id': str(producto['_id']),
                                    'nombre_producto': producto['nombre'],
                                    'cantidad': cantidad_necesaria
                                }]
                            }
                        else:
                            filamentos_necesarios[filamento['_id']]['cantidad_necesaria'] += cantidad_necesaria
                            filamentos_necesarios[filamento['_id']]['productos'].append({
                                'producto_id': str(producto['_id']),
                                'nombre_producto': producto['nombre'],
                                'cantidad': cantidad_necesaria
                            })

                productos_analizados.append({
                    'pedido_id': str(pedido['_id']),
                    'producto_id': str(producto['_id']),
                    'nombre_producto': producto['nombre'],
                    'cantidad': pedido['cantidad']
                })

            # Analizar si hay problemas de stock
            problemas_stock = []
            for filamento_id, info in filamentos_necesarios.items():
                if info['stock_actual'] < info['cantidad_necesaria']:
                    problemas_stock.append({
                        'filamento_id': str(filamento_id),
                        'nombre': info['nombre'],
                        'stock_actual': info['stock_actual'],
                        'cantidad_necesaria': info['cantidad_necesaria'],
                        'diferencia': info['cantidad_necesaria'] - info['stock_actual'],
                        'productos_afectados': info['productos']
                    })

            return {
                'total_pedidos': len(pedidos),
                'total_productos': len(productos_analizados),
                'filamentos_necesarios': filamentos_necesarios,
                'problemas_stock': problemas_stock,
                'productos_analizados': productos_analizados
            }

        except Exception as e:
            print(f"Error al analizar stock de filamentos: {e}")
            return None

    def generar_reporte(self, fecha_entrega):
        """
        Genera un reporte completo para una fecha de entrega específica
        """
        try:
            # Obtener pedidos para la fecha
            pedidos = self.obtener_pedidos_por_fecha(fecha_entrega)
            
            if not pedidos:
                return {
                    'fecha_entrega': fecha_entrega,
                    'mensaje': 'No hay pedidos para esta fecha',
                    'pedidos': [],
                    'analisis_stock': None
                }

            # Analizar stock de filamentos
            analisis_stock = self.analizar_stock_filamentos(pedidos)

            # Generar reporte
            reporte = {
                'fecha_entrega': fecha_entrega,
                'total_pedidos': len(pedidos),
                'pedidos': [{
                    'id': str(pedido['_id']),
                    'cliente': pedido.get('cliente_id'),
                    'producto': pedido.get('producto_id'),
                    'cantidad': pedido.get('cantidad'),
                    'estado': pedido.get('estado')
                } for pedido in pedidos],
                'analisis_stock': analisis_stock,
                'tiene_problemas_stock': len(analisis_stock['problemas_stock']) > 0 if analisis_stock else False
            }

            return reporte

        except Exception as e:
            print(f"Error al generar reporte: {e}")
            return None

    def actualizar_stock_filamentos(self, filamentos_utilizados):
        """
        Actualiza el stock de filamentos después de procesar los pedidos
        """
        try:
            for filamento_id, cantidad in filamentos_utilizados.items():
                self.db.filamentos.update_one(
                    {'_id': ObjectId(filamento_id)},
                    {'$inc': {'stock': -cantidad}}
                )
            return True
        except Exception as e:
            print(f"Error al actualizar stock de filamentos: {e}")
            return False

    def __del__(self):
        """
        Cierra la conexión a MongoDB cuando se destruye la instancia
        """
        if hasattr(self, 'client'):
            self.client.close()
            print("Conexión a MongoDB cerrada") 