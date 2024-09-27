# Mastodon
## Setup
### Mastodon-App-Setup
Setup the App in Mastodon as follows:
* Create a Mastodon Account (if you don’t have one)
** If you haven't already, sign up for an account on a Mastodon instance (e.g., mastodon.social or another instance of your choice).

* Go to "Development" Section
** Log into your Mastodon account.
** Click on your profile icon (usually in the top-right corner).
** Go to Preferences.
** Scroll down to the Development section (or find it in the sidebar).
** Click on Your applications.
* Create a New Application
** Click the New Application button.
** Fill out the form:
** Application Name: Enter a name for your application (e.g., "My Bot").
** Website: You can leave this blank or put your website URL.
** Redirect URI: Leave this as the default (urn:ietf:wg:oauth:2.0:oob unless you need something else.
** Scopes: Select the permissions your application will need, such as:
*** read (if your app only needs to read data)
*** write (if it needs to post to Mastodon)
*** follow (if it needs to follow accounts)
** You can select all if needed.
** Click Submit.
* Obtain the Access Token
** After creating the application, you’ll see the Client Key and Client Secret.
** Scroll down to the section labeled Your access token.
** Copy the access token displayed in this section. This is the token you'll use to authenticate your app or bot with Mastodon.
### AP-Setup 
* create .env file
* define the following constants in the .env file
** MASTODON_API_BASE_URL
** MASTODON_CLIENT_ID
** MASTODON_CLIENT_SECRET
** MASTODON_ACCESS_TOKEN
* if you don't know where to get the constants values, see "Mastodon-APP-Setup"