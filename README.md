# Details

This is an application that can be used to monitor booked southwest flights for
price changes. It logs into the accounts credentials are proided for, and
checks to see if rebooking the flight would result in a lower price. If a lower
price is available it will email you via the mailgun api. It will not
automatically rebook the flight for you. You will need to create a free mailgun
account to be able to receive the email notifications.

# Setup

## Option 1 - Run via Docker (recommended)

1. Install docker
   ([ubuntu](https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository),
[windows](https://docs.docker.com/docker-for-windows/install/),
[osx](https://docs.docker.com/docker-for-mac/install/)

2. Pull docker image

```
docker pull xur17/southwest-alerts
```

3. Run docker image (replacing everything on the right side of the equal sign with your value. You can add additional username#, password#, email# values as needed for additional southwest accounts.

```
docker run -e MAILGUN_API_KEY=??? -e USERNAME1=SOUTHWEST_USERNAME -e PASSWORD1=SOUTHWEST_PASSWORD -e EMAIL1=NOTIFICATION_EMAIL xur17/southwest-alerts
```

## Option 2 - Run natively

1. Pull repository

```
git pull xur17/southwest-alerts
cd southwest-alerts
```

2. Install dependencies

```
pip3 install -r requirements.txt
```

3. Set environment variables (replacing value with the appropriate value)

```
export MAILGUN_API_KEY=VALUE
export USERNAME1=VALUE
export PASSWORD1=VALUE
export EMAIL1=VALUE
```

4. Run

```
python southwestalerts/app.py
```
