FROM eclipse-temurin:8-jdk-jammy@sha256:44ab6db1a674bf1a4af11dd208c92130d61b78d34b3efffc566926c808c3c1d3
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
WORKDIR /opt
COPY NetLogo-6.0.4-64.tgz /opt/
RUN echo '0dcd9df4dfb218826a74f9df42163fa588908a1dfe58864106936f8dfb76acec  NetLogo-6.0.4-64.tgz' | sha256sum -c - && tar xzf NetLogo-6.0.4-64.tgz && ln -s 'NetLogo 6.0.4' netlogo && rm NetLogo-6.0.4-64.tgz
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && pip3 install mysql-connector-python requests
