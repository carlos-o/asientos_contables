# Asientos Contables Test

## Asientos Contables Backend

### **Prerequisitos**

Es necesario crear en la raiz del proyecto un archivo (.env)
y agregar toda la informacion del .env.false

#### **Creación y activación del entorno via docker**

1.- instalar docker [DOCKER](https://docs.docker.com/docker-for-windows/install/)

2.- ir a la carpeta asientos_contables
    
    cd asientos_contables

3.- crear el archivo de configuración

    touch .env
    
copiar la informacion del archivo .env.false

4.- Ejecutar el comando:

    docker-compose build

5.- Ejecutar el comando para levantar el entorno

    docker-compose up
        
6.- Ejecutar las migraciones abrir una nueva terminal y ejecutar el siguiente comando:

    docker exec web python manage.py migrate

7.- url del backend

    http://127.0.0.1:8000

8.- Ejecutar el comando para ejecutar los test

    docker exec web pytest