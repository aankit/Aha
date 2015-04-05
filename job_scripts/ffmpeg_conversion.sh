ffmpeg -i $1 -c:v copy -c:a copy -bsf:a aac_adtstoasc /var/www/replay/videos/$2 
