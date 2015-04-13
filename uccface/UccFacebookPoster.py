#!/u0sr/bin/env
import facepy
import sys
import urllib
import urlparse
import subprocess
import warnings
import readline
import string
import datetime
import pickle
from optparse import OptionParser
DEFAULT_IDENTITY_FILENAME = "identity.pck"

GROUP_ID = '335984893161499' #'197082577000332' 
PAGE_ID = 'universitycomputerclub'


def Authenticate():
    """Returns access-token"""
    APP_ID = 398756193522111
    APP_SECRET = "ad1f8b622d082d2364e960ae7c812619"
    PERMISSIONS=["publish_stream", "user_groups", "user_events", "create_event"]
    
    oauth_args = dict(
        client_id = APP_ID,
        redirect_uri = "http://www.facebook.com/connect/login_success.html",
        scope = string.join(PERMISSIONS, " " ),
        response_type='token' )
            
    oauth_url='http://www.facebook.com/dialog/oauth?'
    full_page_url = oauth_url + urllib.urlencode(oauth_args)

    oauth_response = raw_input("please open: " +    full_page_url + ",\n" +
            "and paste the final URL you are redirected to here: ")
    
    frag = urlparse.urlparse(oauth_response).fragment

    if (frag.startswith("access_token=")):
        token = frag.split("=")[1].split("&")[0]
        return token
    else: raise ValueError("Could not fine access_token string")


class IdentityData:
    _token =""
    
    def token(self):
        return self._token

    def recreate_token(self):
        self._token = Authenticate()
        self.save()
        return self.token()

    def recreate(self):
        self.recreate_token()
        return self
    
    def save(self):
        pickle.dump(self, open(identity_filename, "wb"))


class Poster:
	def formatDatetime(datetime):
		TIMEZONE = str(datetime.tzinfo or "+0800")
		datestring = datetime.strftime("%Y-%m-%dT%H:%M:%S")
		return datestring + TIMEZONE

    def __init__(self, id_filename=DEFAULT_IDENTITY_FILENAME):
        try:
              identity = pickle.load(open(identity_filename) , "rb" ))
        except IOError:
              identity = IdentityData().recreate()
              
    
    def loadgraph(self):
        graph = facepy.GraphAPI(self.__identity.token())
        try:
            #test if still valid
            graph.get(GROUP_ID+"/feed")
        except facepy.exceptions.OAuthError:    
            print("Token Not Valid, reauthenticating")
            self.__identity.recreate_token()
        return graph
		
	def CreateEvent(self,
					name,
					description="",
					startdatetime=datetime.datetime.now(),
					enddatetime= None,
					location="UCC"):
		graph = loadgraph()

		data = dict(name=name, 
					description=description,
					start_time=formatDatetime(startdatetime),
					page_id=GROUP_ID)
		if (enddatetime is not None): data['end_time'] = formatDatetime(enddatetime)

		if (location.upper()=="UCC" or location.upper() =="UCC CLUBROOM"):
			data['location_id'] = graph.get(PAGE_ID)['id']
		else:
			data['location']=location

		print(str(data))
		graph.post(GROUP_ID + '/events',retry=0,**data)
		print("Event Posted successfully")


	def PostMessage(self, message, link=None):
		graph = loadgraph()
		if (message):
			
			if (link): 
				ret=graph.post(GROUP_ID + "/feed", message=message, link=link)
			else:
				ret= graph.post(GROUP_ID + "/feed", message=message)
		print("Message Posted successfully")
	else:
		print("No message")
		ret = -1
	return ret



if __name__ == "__main__":
	parser = OptionParser(usage = "%prog message [options]\nAutomatically posts to the UCC facebook group.\nTo change who the App posts as,\ndelete " ++ " which will force a reauthentication.",
						  epilog = "Can also be opened as a python library for more functionality")
	parser.add_option("-l", "--link",
					  metavar="URL",
					  help="attach a link to URL to the message.")
	(options, args) = parser.parse_args()

	msg = " ".join(args)
	link = options.link
	PostMessage(msg, link)




