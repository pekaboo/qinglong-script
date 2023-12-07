
upstream euexp {
	ip_hash;
	server app6.lo:8088;
	keepalive 30;
}

server {
    listen 80;
    server_name eu-exp.cn;
    access_log /var/log/nginx/euexp-access.log;
    error_log /var/log/nginx/euexp-error.log;
    return 301 https://$host$request_uri;
}

server {
	listen       80;
	server_name  tms.eu-exp.cn;
	access_log /var/log/nginx/access-tms.log main;
	error_log /var/log/nginx/error-tms.log;
	location / {
		rewrite ^(.*)$ https://center.eu-exp.cn permanent;
	}
}

server {
    listen 443 ssl;
    server_name eu-exp.cn;
    ssl_certificate /etc/nginx/cert/eu-exp/eu-exp.cn.pem;
    ssl_certificate_key /etc/nginx/cert/eu-exp/eu-exp.cn.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    access_log /var/log/nginx/euexp-access443.log;
    error_log /var/log/nginx/euexp-err443.log;

    #解决cms在客户浏览器的缓存问题
	location /cms {
        rewrite ^(.*) https://www.eu-exp.cn permanent;
    }

	location /ru {
		rewrite ^(.*) https://ru.eu-exp.cn/ permanent;	
	}

	location /fba {
		rewrite ^(.*) https://center.eu-exp.cn/ permanent;
	}

	location /tms {
		rewrite ^(.*) https://center.eu-exp.cn/ permanent;
	}

	location /wlms {
		rewrite ^(.*) https://center.eu-exp.cn/ permanent;
	}
	
    location /personal/message/pending/count {
		proxy_pass http://euexp/personal/message/pending/count/;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
	}

	location /images {
		access_log off;
		proxy_pass http://euexp/images/;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
    	}

	location /service/track {
		proxy_pass http://euexp;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
	}

	location / {
		proxy_pass http://data.lo:92;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
	}

	location /track/aliexpress {
		proxy_pass http://euexp;
	}
	
	location /order/track {
		if ($query_string ~* "cno=(.*)$"){
			set $num $1;
			rewrite ^(.*) https://www.eu-exp.cn/service/track?waybillNum=$num? permanent;
		}
		rewrite ^(.*) https://www.eu-exp.cn/service/track?waybillNum=? permanent;
	}

	location ~ ^(/doc/j-net-o-api-new.html|/doc/j-net-o-api.html|/doc/j-net-w-api.html|/css/service.css|/css/glyphicons/.*|/js/layui/css/layui.css|/js/jquery-1.7.1.min.js|/js/layer/layer.js|/js/layui/css/layui.css)$ {
		proxy_pass http://euexp;
		proxy_http_version 1.1;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
	}
}



upstream gateway {
	server data.lo:81;
	server app4.lo:81;
	keepalive 30;
}


server {
    listen 80;
    server_name gateway.* center.* control-server.* tms-server.* fba-server.* wlms-server.* pay-server.* csc-server.* wlms-api.* tms-api.* pay-api.* fba-api.* fs.* api2.* nm.* pda.* tms-ui-control.*;
    access_log /var/log/nginx/euexp-access.log;
    error_log /var/log/nginx/euexp-error.log;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name gateway.* center.* control-server.* tms-server.* fba-server.* wlms-server.* pay-server.* csc-server.* wlms-api.* tms-api.* pay-api.* fba-api.* fs.* api2.* nm.* pda.* tms-ui-control.*;

	ssl_certificate /etc/nginx/cert/eu-exp/center.eu-exp.cn.pem;
    ssl_certificate_key /etc/nginx/cert/eu-exp/center.eu-exp.cn.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    access_log /var/log/nginx/euexp-access443.log;
    error_log /var/log/nginx/euexp-err443.log;



	location / {
		proxy_pass http://gateway;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $host;
	}
}
