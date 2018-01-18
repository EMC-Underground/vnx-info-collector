FROM centos:latest

MAINTAINER Craig J Smith <craig.j.smith@dell.com>

COPY ./NaviCLI-Linux-64-x86-en_US-7.33.9.1.84-1.x86_64.rpm /tmp

COPY ./requirements.txt /

RUN yum -y update; yum clean all && \
    yum -y install epel-release ca-certificates; yum clean all && \
    yum -y install python-pip; yum clean all && \
    rm -rf /var/cache/yum && \
    pip install --upgrade pip && \
    rpm -i /tmp/NaviCLI-Linux-64-x86-en_US-7.33.9.1.84-1.x86_64.rpm && \
    echo "low" > /opt/Navisphere/bin/setlevel.log && \
    /opt/Navisphere/bin/setlevel_cli.sh && \
    pip install -r requirements.txt

RUN update-ca-trust force-enable

COPY ./ca.crt /etc/pki/ca-trust/source/anchors

RUN update-ca-trust extract

COPY ./collector.py /

CMD ["/collector.py"]
