FROM debian:buster-slim AS vulnerable-user

RUN apt update && apt install -y postgresql-client openssh-server openssl
RUN sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
RUN sed -i 's/ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/g' /etc/ssh/sshd_config
RUN useradd -p $(openssl passwd -1 password) -m victim
RUN echo "1 git push\n2 tail -f var/logs/error\n3 nano +22,5 functions.sh\n4 PGPASSWORD=dbpassword psql -h 192.168.94.21 -U dbuser beastdb\n5 source project-env/bin/activate\n6 history" >> /home/victim/.bash_history

ENTRYPOINT [ "sh", "-c", "service ssh start && tail -f /dev/null" ]
