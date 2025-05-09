from flask import Blueprint, request, jsonify
from models.print_job import PrintJob
from bson import ObjectId

print_jobs = Blueprint('print_jobs', __name__)

@print_jobs.route('/api/print-jobs', methods=['GET'])
def get_print_jobs():
    from app import mongo
    jobs = mongo.db.print_jobs.find()
    return jsonify([PrintJob.from_dict(job).to_dict() for job in jobs])

@print_jobs.route('/api/print-jobs', methods=['POST'])
def create_print_job():
    from app import mongo
    data = request.json
    print_job = PrintJob(
        name=data['name'],
        description=data['description'],
        file_url=data['file_url']
    )
    result = mongo.db.print_jobs.insert_one(print_job.to_dict())
    return jsonify({'message': 'Print job created', 'id': str(result.inserted_id)}), 201

@print_jobs.route('/api/print-jobs/<job_id>', methods=['GET'])
def get_print_job(job_id):
    from app import mongo
    job = mongo.db.print_jobs.find_one({'_id': job_id})
    if job:
        return jsonify(PrintJob.from_dict(job).to_dict())
    return jsonify({'message': 'Print job not found'}), 404

@print_jobs.route('/api/print-jobs/<job_id>', methods=['PUT'])
def update_print_job(job_id):
    from app import mongo
    data = request.json
    job = mongo.db.print_jobs.find_one({'_id': job_id})
    if job:
        updated_job = PrintJob.from_dict(job)
        updated_job.status = data.get('status', updated_job.status)
        updated_job.name = data.get('name', updated_job.name)
        updated_job.description = data.get('description', updated_job.description)
        mongo.db.print_jobs.update_one(
            {'_id': job_id},
            {'$set': updated_job.to_dict()}
        )
        return jsonify({'message': 'Print job updated'})
    return jsonify({'message': 'Print job not found'}), 404

@print_jobs.route('/api/print-jobs/<job_id>', methods=['DELETE'])
def delete_print_job(job_id):
    from app import mongo
    result = mongo.db.print_jobs.delete_one({'_id': job_id})
    if result.deleted_count:
        return jsonify({'message': 'Print job deleted'})
    return jsonify({'message': 'Print job not found'}), 404 