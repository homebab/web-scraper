```
   ,-,--.    _,.----.                ,---.          _ __       ,----.               
 ,-.'-  _\ .' .' -   \  .-.,.---.  .--.'  \      .-`.' ,`.  ,-.--` , \  .-.,.---.   
/==/_ ,_.'/==/  ,  ,-' /==/  `   \ \==\-/\ \    /==/, -   \|==|-  _.-` /==/  `   \  
\==\  \   |==|-   |  .|==|-, .=., |/==/-|_\ |  |==| _ .=. ||==|   `.-.|==|-, .=., | 
 \==\ -\  |==|_   `-' \==|   '='  /\==\,   - \ |==| , '=',/==/_ ,    /|==|   '='  / 
 _\==\ ,\ |==|   _  , |==|- ,   .' /==/ -   ,| |==|-  '..'|==|    .-' |==|- ,   .'  
/==/\/ _ |\==\.       /==|_  . ,'./==/-  /\ - \|==|,  |   |==|_  ,`-._|==|_  . ,'.  
\==\ - , / `-.`.___.-'/==/  /\ ,  )==\ _.\=\.-'/==/ - |   /==/ ,     //==/  /\ ,  ) 
 `--`---'             `--`-`--`--' `--`        `--`---'   `--`-----`` `--`-`--`--'  
```

## Get Started
- run app
swagger: http://localhost:9000/
```
python manager.py run
```
- test
```
python manager.py test
```
## Setup on Mac
### chromedriver
- install chromedriver
```shell script
brew install chromedriver
brew install Caskroom/versions/google-chrome-canary
```
- set environment variable `$CHORME_DRIVER`. ex `/usr/local/bin/chromedriver`
### aws configure
- aws configure with ur IAM Key
```shell script
# if you don't have awscli, pip install awscli
aws configure
```
### youtube api key
- set environment variable `$YOUTUBE_API_KEY`
