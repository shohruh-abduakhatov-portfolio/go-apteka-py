cd /var/www/pharmex_client/ &&
git pull &&
git submodule update --init --force --remote -- modules/kinetic_core &&
git submodule update --init --force --remote -- modules/business &&
git submodule update --init --force --remote -- modules/pharmex &&
git rev-parse HEAD > head &&
git log -1 --format=%cd > head_date &&
echo 'staring project'
python3.7 /var/www/pharmex_client/web/main.py