from flask import Flask,request, jsonify
from flask_socketio import SocketIO, emit, send
from bs4 import BeautifulSoup
from global_state import globalStateMgr
from workflow_runner import WorkflowRunner
from socketio_instance import socketio
from flask_restful import Api
from llm import LLMHandler
from html_handler import HTMLHandler
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key!'
socketio.init_app(app)

@socketio.on('connect')
def test_connect():
    print('Client connected')
    

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('new_work')
def new_work(data):
    try:
        print('new work received')
        print('data', data)
        
        # Validate required data
        if not data.get('work_id') or not data.get('renderedHTML'):
            raise ValueError("Missing required fields: work_id or renderedHTML")
            
        wr = WorkflowRunner(data['work_id'], data['renderedHTML'])
        wr.set_context_from_file("./context.txt")
        globalStateMgr.add_workflow_runner(data['work_id'], wr)
        wr.run()
        
        # Success response
        emit("end-process", data)
        
    except FileNotFoundError as e:
        error_data = {
            'work_id': data.get('work_id'),
            'error': 'Context file not found',
            'details': str(e)
        }
        emit("end-process", error_data)
        
    except ValueError as e:
        error_data = {
            'work_id': data.get('work_id'),
            'error': 'Invalid input data',
            'details': str(e)
        }
        emit("end-process", error_data)
        
    except Exception as e:
        error_data = {
            'work_id': data.get('work_id'),
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }
        emit("end-process", error_data)
        print(f"Error in new_work: {traceback.format_exc()}")


@app.route('/api/select_option', methods=['POST'])
def get_option_to_select():
    data = request.get_json()
    wr = globalStateMgr.get_workflow_runner(data['work_id'])
    if wr == None:
        return jsonify({'status': 'unsuccessful'})
    option_text = LLMHandler().select_drop_down(wr.context,data['description'],data['options'])
    new_html_handler = HTMLHandler(data['newHtml'])
    element_to_select = new_html_handler.get_element_with_text(option_text)
    if(element_to_select==None):
        return jsonify({'status': 'unsuccessful'})
    return jsonify({'status': 'success', 'element_to_select': element_to_select,'work_id':data['work_id']})

if __name__ == '__main__':
  socketio.run(app, debug=True,port=5001)
