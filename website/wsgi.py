import sys
project_home = '/home/ShaWmgxe4/grrc_final/website/app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GRRC.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
