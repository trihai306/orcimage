module.exports = {
  apps: [{
    name: 'ocr-server',
    script: 'venv/bin/python',
    args: '-m app.main',
    cwd: '/www/wwwroot/your-domain.com', // Thay đổi đường dẫn theo domain của bạn
    interpreter: 'none',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 8000
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
}

