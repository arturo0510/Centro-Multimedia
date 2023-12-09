#!/bin/bash

# Actualizar la lista de paquetes
sudo apt-get update

# Actualizar todos los paquetes instalados
sudo apt-get upgrade

# Instalar ffmpeg, vlc, python3-vlc, python3-pyudev y wget
sudo apt -y install ffmpeg vlc python3-vlc python3-pyudev wget

# Instalar python3-tk
sudo apt-get install python3-tk

# Instalar la biblioteca Pillow con pip
pip install Pillow

# Instalar libwidevinecdm0
sudo apt install libwidevinecdm0 -y
