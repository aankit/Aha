sudo apt-get install build-essential libpcre3 libpcre3-dev libssl-dev
wget http://nginx.org/download/nginx-1.7.11.tar.gz
wget https://github.com/arut/nginx-rtmp-module/archive/master.zip
tar -zxvf nginx-1.7.11.tar.gz
unzip master.zip
cd nginx-1.7.11
./configure --with-http_ssl_module --add-module=../nginx-rtmp-module-master
make
sudo make install