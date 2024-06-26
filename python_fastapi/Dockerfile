FROM docker.repo.eng.netapp.com/rhel8/podman:8.9-1
USER root


# Install the needed tools and libraries
# Install the needed PKCS libraries for the OS
RUN yum update -y && \
    yum install wget unzip tar make pcsc-lite-libs -y

# Install the HSM DPOD client
RUN mkdir -p /root/HSM_DPOD && mkdir -p /tmp/HSM_DPOD
COPY setup-JarCodeSigner_Mar2024.zip  /tmp/HSM_DPOD
RUN cd /tmp/HSM_DPOD && \
    unzip setup-JarCodeSigner_Mar2024.zip && \
    tar -xvf cvclient-min.tar && \
    cp -Rf /tmp/HSM_DPOD/* /root/HSM_DPOD && \
    rm -rf /tmp/HSM_DPOD && \
    rm -f /root/HSM_DPOD/setup-JarCodeSigner_Mar2024.zip && \
    chmod -Rf 755 /root/HSM_DPOD/* && cp /root/HSM_DPOD/Chrystoki.conf /etc/Chrystoki.conf

# disable subscription-manager plugin
RUN sed -i 's/enabled=1/enabled=0/g' /etc/yum/pluginconf.d/subscription-manager.conf
RUN yum clean all

# Install the Cosign tool for Docker Image signing
RUN wget -O /usr/local/bin/cosign "https://github.com/sigstore/cosign/releases/download/v1.13.1/cosign-linux-pivkey-pkcs11key-amd64" && \
    chmod +x /usr/local/bin/cosign

# Verify the installation of Cosign
RUN cosign version


# Set the Environment variables for the DPOD Client
WORKDIR /root/HSM_DPOD
RUN source ./setenv
RUN echo "cd /root/HSM_DPOD && source ./setenv && cd /dpod" >> ~/.bashrc


# Install the Docker Client
RUN dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
RUN dnf install docker-ce-cli --nobest --allowerasing -y



# Install python3.10.0
RUN yum install gcc openssl-devel bzip2-devel libffi-devel -y
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
    tar xvf Python-3.10.0.tgz && \
    cd Python-3.10.0 && \
    ./configure --enable-optimizations && \
    make install altinstall &&\
    python3.10 --version

# Install the pip for the python3.10
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.10 get-pip.py && \
    pip3.10 --version

# Install the requirements for the FastAPI application
WORKDIR /dpod
COPY startup-uvicorn.sh /dpod
COPY ./requirements.txt /dpod/requirements.txt
RUN pip3.10 install --no-cache-dir --upgrade -r /dpod/requirements.txt
COPY ./app /dpod/app

# start the FastAPI application
ENTRYPOINT ["/bin/bash", "/dpod/startup-uvicorn.sh",]

#End of the Dockerfile
