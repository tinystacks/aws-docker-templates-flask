from app import app
import os 

if __name__ == '__main__':
    stage = os.environ.get('STAGE', 'local')
    the_port = 8000 if stage=='local' else 80
    app.run(host='0.0.0.0', port=the_port)