from streamlit import config as _config
from streamlit.web.bootstrap import run
_config.set_option("server.headless", True)
run('main.py', args=[], flag_options=[], is_hello=False)