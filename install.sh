#!/bin/bash
cd ~
echo '
─────────███─────────
─────────█$█─────────
─────█████$██████────
───███████$████████──
──████████$████████──
─█████████$████████──
─███████─█$█──████───
─███████─█$█─────────
─█████████$█─────────
─█████████$█████─────
──████████$███████───
────██████$█████████─
───────███$█████████─
─────────█$█─████████
─────────█$█──███████
──████───█$█──███████
─█████████$█████████─
██████████$█████████─
─█████████$████████──
───███████$██████────
─────────█$█─────────
─────────███─────────

Plutus Binom Cost Synchronizer

Starting installation...
'
sudo apt install git python3 python3-pip &> /dev/null
git clone https://github.com/piotrusin/binom-cost-synchronizer.git &> /dev/null
cd binom-cost-synchronizer
pip3 install pipenv &> /dev/null
pipenv install &> /dev/null
crontab -l > mycron
echo "10 0 * * * /usr/local/bin/pipenv run python $PWD/sync.py > $PWD/cron.log 2>&1" >> mycron
crontab mycron
rm mycron
echo '#!/bin/bash
echo -n "Binom Domain (https://your-domain.com): "
read BINOM_DOMAIN </dev/tty
echo "CS_BINOM_DOMAIN=$BINOM_DOMAIN" >> .env
echo -n "Binom API Key (39 characters): "
read BINOM_API_KEY </dev/tty
echo "CS_BINOM_API_KEY=$BINOM_API_KEY" >> .env
echo -n "PropellerAds API Key (48 characters): "
read PROPELLER_ADS_API_KEY </dev/tty
echo "CS_PROPELLER_ADS_API_KEY=$PROPELLER_ADS_API_KEY" >> .env
echo -n "UTC Timezone (number from -12 to 14): "
read TIMEZONE </dev/tty
echo "CS_TIMEZONE=$TIMEZONE" >> .env' > configure.sh

echo 'Done.

Initializing configuration:
'

chmod +x configure.sh &> /dev/null
bash ./configure.sh
rm -rf ./configure.sh &> /dev/null
echo "Installation finished. Verify if API keys are correct. You can change them in ~/binom-cost-synchronizer/.env"
cat .env