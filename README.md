So this little app works on the port 3000 and has a 5000 UDP port
if you want to see your data on your computer when running a container, you should use next command

docker run -d -p 127.0.0.1:5000:5000/udp -p 3000:3000 -v full_folder_path:/app/storage image_name

where full_folder_path is a path to your folder in your system
and image_name it's obviously the name of an image