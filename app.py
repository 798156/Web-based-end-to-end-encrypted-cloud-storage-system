from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app, supports_credentials=True) # 允许跨域
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# --- 数据库配置 (请修改此处) ---
# 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
# 示例: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/cloud_storage'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@localhost:3306/cloud_storage'
# 如果还未配置好 MySQL，可以先用下面这行 SQLite (默认)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 存储用于验证登录的哈希（服务端哈希，不是客户端派生的密钥）
    auth_hash = db.Column(db.String(128), nullable=False)
    # 存储用户的公钥 (PEM格式)
    public_key = db.Column(db.Text, nullable=False)
    # 存储加密后的私钥 (Base64格式)，只有用户知道密码才能解密
    encrypted_private_key = db.Column(db.Text, nullable=False)
    # 存储用户注册时的随机盐 (Hex格式)，用于客户端密钥派生
    salt = db.Column(db.String(64), nullable=False)
    # 用户头像文件名 (相对于 UPLOAD_FOLDER 或 static/avatars)
    avatar = db.Column(db.String(255), nullable=True, default='default-avatar.png')

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Add relationship
    owner = db.relationship('User', backref=db.backref('files', lazy=True))
    # 加密后的文件名 (Base64)
    encrypted_name = db.Column(db.Text, nullable=False)
    # 加密后的文件密钥 (Base64) - 用用户公钥加密的AES密钥
    encrypted_key = db.Column(db.Text, nullable=False)
    # AES加密用的IV (Hex)
    iv = db.Column(db.String(32), nullable=False)
    # 物理存储的文件名
    storage_filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 用接收者公钥加密的 AES 密钥 (Base64)
    encrypted_key = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    file = db.relationship('File', backref=db.backref('shares', cascade='all, delete-orphan'))
    recipient = db.relationship('User', foreign_keys=[recipient_id])

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False) # UPLOAD, DOWNLOAD, SHARE, DELETE
    details = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized'}), 401

# --- Routes ---

@app.route('/')
def index():
    return "Backend API Server Running"

# API: Register
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    new_user = User(
        username=data['username'],
        auth_hash=data['auth_hash'], # 客户端发送的密码哈希
        public_key=data['public_key'],
        encrypted_private_key=data['encrypted_private_key'],
        salt=data['salt']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful'})

# API: Login Challenge (Get Salt)
@app.route('/api/get_salt', methods=['POST'])
def api_get_salt():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'salt': user.salt})

# API: Login Verify
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    # 简单的密码验证，实际生产应使用更安全的比对
    if user and user.auth_hash == data['auth_hash']:
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'encrypted_private_key': user.encrypted_private_key,
            'public_key': user.public_key
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

# API: Upload File
@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    encrypted_name = request.form.get('encrypted_name')
    encrypted_key = request.form.get('encrypted_key')
    iv = request.form.get('iv')
    
    if file:
        # Generate a safe filename for storage
        storage_filename = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], storage_filename)
        file.save(file_path)
        
        new_file = File(
            user_id=current_user.id,
            encrypted_name=encrypted_name,
            encrypted_key=encrypted_key,
            iv=iv,
            storage_filename=storage_filename,
            mime_type=file.content_type,
            size=os.path.getsize(file_path)
        )
        db.session.add(new_file)
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='UPLOAD', details=f'Uploaded file (ID: {new_file.id})', ip_address=request.remote_addr)
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully'})
    return jsonify({'error': 'Upload failed'}), 500

from datetime import datetime

# API: List Files
@app.route('/api/files')
@login_required
def api_list_files():
    files = File.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    return jsonify([{
        'id': f.id,
        'encrypted_name': f.encrypted_name,
        'encrypted_key': f.encrypted_key,
        'iv': f.iv,
        'mime_type': f.mime_type,
        'size': f.size,
        'created_at': f.created_at.isoformat()
    } for f in files])

# API: Download File
@app.route('/api/download/<int:file_id>')
@login_required
def api_download(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Log action
    log = AuditLog(user_id=current_user.id, action='DOWNLOAD', details=f'Downloaded file (ID: {file.id})', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()

    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], file.storage_filename),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='encrypted_file.bin' # 实际文件名由前端解密后重命名
    )

# API: Soft Delete File
@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
def api_delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        file.is_deleted = True
        file.deleted_at = datetime.utcnow()
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='DELETE', details=f'Moved file to recycle bin (ID: {file.id})', ip_address=request.remote_addr)
        db.session.add(log)

        db.session.commit()
        return jsonify({'message': 'File moved to recycle bin'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: List Recycle Bin Files
@app.route('/api/recycle_bin')
@login_required
def api_list_recycle_bin():
    files = File.query.filter_by(user_id=current_user.id, is_deleted=True).order_by(File.deleted_at.desc()).all()
    return jsonify([{
        'id': f.id,
        'encrypted_name': f.encrypted_name,
        'size': f.size,
        'deleted_at': f.deleted_at.isoformat() if f.deleted_at else None
    } for f in files])

# API: Restore File
@app.route('/api/files/<int:file_id>/restore', methods=['POST'])
@login_required
def api_restore_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    file.is_deleted = False
    file.deleted_at = None
    
    # Log action
    log = AuditLog(user_id=current_user.id, action='RESTORE', details=f'Restored file (ID: {file.id})', ip_address=request.remote_addr)
    db.session.add(log)
    
    db.session.commit()
    return jsonify({'message': 'File restored successfully'})

# API: Permanent Delete File
@app.route('/api/files/<int:file_id>/permanent', methods=['DELETE'])
@login_required
def api_permanent_delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Delete physical file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.storage_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='PERMANENT_DELETE', details=f'Permanently deleted file (ID: {file.id})', ip_address=request.remote_addr)
        db.session.add(log)

        # Delete database record
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File permanently deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get Public Key
@app.route('/api/users/public_key', methods=['POST'])
@login_required
def api_get_public_key():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'public_key': user.public_key, 'user_id': user.id})

# API: Get Current User Info
@app.route('/api/me')
@login_required
def api_me():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'avatar': current_user.avatar,
        'created_at': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
    })

# API: Upload Avatar
@app.route('/api/upload_avatar', methods=['POST'])
@login_required
def api_upload_avatar():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400

        # Save file
        filename = secure_filename(f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}")
        
        # Ensure static/avatars exists
        avatar_dir = os.path.join(app.root_path, 'static', 'avatars')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
            
        file.save(os.path.join(avatar_dir, filename))
        
        # Update user record
        # Remove old avatar if it's not default
        if current_user.avatar and current_user.avatar != 'default-avatar.png':
            old_path = os.path.join(avatar_dir, current_user.avatar)
            if os.path.exists(old_path):
                os.remove(old_path)
                
        current_user.avatar = filename
        db.session.commit()
        
        return jsonify({'message': 'Avatar updated', 'avatar': filename})
    
    return jsonify({'error': 'Upload failed'}), 500

# API: Change Password
@app.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    data = request.json
    old_auth_hash = data.get('old_auth_hash')
    new_auth_hash = data.get('new_auth_hash')
    new_encrypted_private_key = data.get('new_encrypted_private_key')
    
    # 1. Verify old password
    if current_user.auth_hash != old_auth_hash:
        return jsonify({'error': 'Incorrect old password'}), 401
        
    # 2. Update password and re-encrypted private key
    try:
        current_user.auth_hash = new_auth_hash
        current_user.encrypted_private_key = new_encrypted_private_key
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='CHANGE_PASSWORD', details='User changed password and re-encrypted private key', ip_address=request.remote_addr)
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Update Username
@app.route('/api/update_username', methods=['POST'])
@login_required
def api_update_username():
    data = request.json
    new_username = data.get('username')
    
    if not new_username or len(new_username.strip()) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
    if new_username == current_user.username:
        return jsonify({'message': 'No change'})
        
    # Check if username exists
    if User.query.filter_by(username=new_username).first():
        return jsonify({'error': 'Username already taken'}), 400
        
    try:
        old_username = current_user.username
        current_user.username = new_username
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='UPDATE_PROFILE', details=f'Changed username from {old_username} to {new_username}', ip_address=request.remote_addr)
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'message': 'Username updated', 'username': new_username})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Share File
@app.route('/api/share', methods=['POST'])
@login_required
def api_share_file():
    data = request.json
    file_id = data.get('file_id')
    recipient_id = data.get('recipient_id')
    encrypted_key = data.get('encrypted_key')
    
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    share = Share(
        file_id=file_id,
        recipient_id=recipient_id,
        encrypted_key=encrypted_key
    )
    db.session.add(share)
    
    # Log action
    log = AuditLog(user_id=current_user.id, action='SHARE', details=f'Shared file (ID: {file.id}) with User (ID: {recipient_id})', ip_address=request.remote_addr)
    db.session.add(log)
    
    db.session.commit()
    return jsonify({'message': 'File shared successfully'})

# API: List Shared Files
@app.route('/api/shared_files')
@login_required
def api_list_shared_files():
    shares = Share.query.filter_by(recipient_id=current_user.id).all()
    return jsonify([{
        'id': s.id,
        'file_id': s.file.id,
        'encrypted_name': s.file.encrypted_name,
        'encrypted_key': s.encrypted_key, # Key encrypted for recipient
        'iv': s.file.iv,
        'size': s.file.size,
        'owner_username': s.file.owner.username, 
        'created_at': s.created_at.isoformat()
    } for s in shares])

# API: List Sent Shares (My Shared Files)
@app.route('/api/sent_shares')
@login_required
def api_list_sent_shares():
    # Join Share with File to find shares where the file belongs to current_user
    shares = db.session.query(Share).join(File).filter(File.user_id == current_user.id).all()
    return jsonify([{
        'id': s.id,
        'file_id': s.file.id,
        'encrypted_name': s.file.encrypted_name,
        'recipient_username': s.recipient.username,
        'created_at': s.created_at.isoformat()
    } for s in shares])

# API: Revoke Share
@app.route('/api/shares/<int:share_id>', methods=['DELETE'])
@login_required
def api_revoke_share(share_id):
    share = Share.query.get_or_404(share_id)
    # Ensure the current user is the owner of the file being shared
    if share.file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Log action
        log = AuditLog(user_id=current_user.id, action='REVOKE_SHARE', details=f'Revoked share of file (ID: {share.file.id}) from user (ID: {share.recipient_id})', ip_address=request.remote_addr)
        db.session.add(log)
        
        db.session.delete(share)
        db.session.commit()
        return jsonify({'message': 'Share revoked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Rename File
@app.route('/api/files/<int:file_id>/rename', methods=['PUT'])
@login_required
def api_rename_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    new_encrypted_name = data.get('encrypted_name')
    
    if not new_encrypted_name:
        return jsonify({'error': 'New name required'}), 400
        
    try:
        file.encrypted_name = new_encrypted_name
        
        # Log action
        log = AuditLog(user_id=current_user.id, action='RENAME', details=f'Renamed file (ID: {file.id})', ip_address=request.remote_addr)
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'message': 'File renamed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Download Shared File
@app.route('/api/download_shared/<int:share_id>')
@login_required
def api_download_shared(share_id):
    share = Share.query.get_or_404(share_id)
    if share.recipient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Log action
    log = AuditLog(user_id=current_user.id, action='DOWNLOAD_SHARED', details=f'Downloaded shared file (ID: {share.file.id})', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], share.file.storage_filename),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='encrypted_shared_file.bin'
    )

# API: Get Audit Logs
@app.route('/api/logs')
@login_required
def api_get_logs():
    logs = AuditLog.query.filter_by(user_id=current_user.id).order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify([{
        'action': l.action,
        'details': l.details,
        'ip': l.ip_address,
        'created_at': l.created_at.isoformat()
    } for l in logs])

# API: Get Analysis Data
@app.route('/api/analysis')
@login_required
def api_get_analysis():
    # 1. Total Storage Used
    total_size = db.session.query(db.func.sum(File.size)).filter_by(user_id=current_user.id).scalar() or 0
    
    # 2. File Count
    file_count = File.query.filter_by(user_id=current_user.id).count()
    
    # 3. File Type Distribution (by MIME type)
    # Group by mime_type and count
    type_stats = db.session.query(File.mime_type, db.func.count(File.id)).filter_by(user_id=current_user.id).group_by(File.mime_type).all()
    
    # Process types for better display
    type_distribution = {}
    for mime, count in type_stats:
        # Simplify mime type (e.g., image/jpeg -> Image)
        simple_type = 'Other'
        if mime:
            if mime.startswith('image/'):
                simple_type = 'Image'
            elif mime.startswith('video/'):
                simple_type = 'Video'
            elif mime.startswith('audio/'):
                simple_type = 'Audio'
            elif mime.startswith('text/') or 'pdf' in mime:
                simple_type = 'Document'
        
        type_distribution[simple_type] = type_distribution.get(simple_type, 0) + count

    return jsonify({
        'total_size': total_size,
        'file_count': file_count,
        'type_distribution': [{'name': k, 'value': v} for k, v in type_distribution.items()]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
