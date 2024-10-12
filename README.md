# ansAI
A python script powered by Google AI Studio and Beautifulsoup that fetches news from ANSA (Italian National Associated Press Agency) and then writes an overview of every category into a markdown file along with sources and a translation in the desired language. 

# installation

#### Clone the repository and get into its folder
```
git clone https://github.com/RubenSab/ansAI.git
cd ansAI/
```
#### Create a virtual environment to install dependencies into (optional)
```
python3 -m venv venv
```
#### Activate the virtual envirnoment (optional)
```
source venv/bin/activate
```
#### Install required dependencies
```
pip install -r requirements.txt
```


# Configuration (necessary)

## Get your API key from Google AI Studio (it's free)
Go to https://aistudio.google.com/app/apikey and press 'create API key',
then open `config.json` and paste it in `"api_key"`'s value.

## Set the news folder path
while in `config.json` write your desided news folder path in `"news_folder_path"`'s value.
####


# Usage
- make sure to have your virtual environment activated if you installed the required dependencies into it
- run ansAI by writing `python3 ansAI.pt`
