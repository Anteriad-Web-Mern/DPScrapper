from flask import Flask
from flask_cors import CORS
import logging
from threading import Thread
import fetch_data

from routes.core_routes import core_bp
from routes.kinsta import kinsta_bp
from routes.dashboard import dashboard_bp
from routes.task import task_bp
from routes.visualization import viz_bp
from routes.results import results_bp
from routes.scraping import scraping_bp
from routes.analytics import analytics_bp

app = Flask(__name__, template_folder="templates")
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register blueprints
app.register_blueprint(core_bp)
app.register_blueprint(kinsta_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(task_bp)
app.register_blueprint(viz_bp)
app.register_blueprint(results_bp)
app.register_blueprint(scraping_bp)
app.register_blueprint(analytics_bp)

if __name__ == "__main__":
    Thread(target=fetch_data.run_fetch).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
