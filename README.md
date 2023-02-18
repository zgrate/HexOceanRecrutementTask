# IMAGE UPLOADER

This app allows user to upload photos using API and retrieve them using REST API

## API DOCS: 
Apidocs are available here https://documenter.getpostman.com/view/23671990/2s93CHuEq2

## Installation instruction:
1. ``git pull https://github.com/zgrate/HexOceanRecrutementTask.git && cd HexOceanRecrutementTask``
2. **SET UP ENVS, ESPECIALLY SECRET_TOKEN**
3. ``docker compose build && docker compose up -d``
4. **FIRST SETUP ONLY** ``docker exec hexoceanrecrutementtask-django_image_api-1 sh init_system.sh``. 
This will create superuser with login *admin* password *admin* and start tiers. **CHANGE PASSWORD ASAP**
5. Your service should work on http://ip_adress:8000

Administration can be done using  http://ip_adress:8000/admin endpoints. You can modify Users and change their tiers in a Users. You can also add new tiers and new allowed sizes there.

