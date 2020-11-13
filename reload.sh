#!/bin/bash
pwd
pip3.7 install -r ../requirements.txt
systemctl --user restart client.pharmex.uz.service;