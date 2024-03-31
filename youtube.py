from google_apis import create_service


class YouTube:
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube']

    def __init__(self, client_file, chat_id=None):
        self.client_file = client_file
        self.chat_id = chat_id
        self.service = None

    def init_service(self):
        self.service = create_service(self.client_file, self.API_NAME, self.API_VERSION, self.chat_id, self.SCOPES)

    def list_channel_subscriptions(self, channel_id, filter_channels=None, order_by='alphabetical'):
        """
        order_by: {alphabetical;relevance;unread}
        """
        subscriptions = []
        try:
            response = self.service.subscriptions().list(
                channelId=channel_id,
                part='snippet',
                forChannelId=filter_channels,
                maxResults=50,
                order=order_by
            ).execute()

            subscriptions.extend(response.get('items'))
            next_page_token = response.get('nextPageToken')

            while next_page_token:
                response = self.service.subscriptions().list(
                    channelId=channel_id,
                    part='snippet',
                    forChannelId=filter_channels,
                    maxResults=50,
                    order=order_by,
                    pageToken=next_page_token
                ).execute()
                subscriptions.extend(response.get('items'))
                next_page_token = response.get('nextPageToken')
            return subscriptions
        except Exception as e:
            print(e.error_details[0]['message'])
            return None

    def list_subscriptions(self, filter_channels=None):
        subscriptions = []
        response = self.service.subscriptions().list(
            mine=True,
            part='snippet',
            forChannelId=filter_channels,
            maxResults=50,
            order='alphabetical'
        ).execute()

        subscriptions.extend(response.get('items'))
        next_page_token = response.get('nextPageToken')

        while next_page_token:
            response = self.service.subscriptions().list(
                mine=True,
                part='snippet',
                forChannelId=filter_channels,
                maxResults=50,
                order='alphabetical',
                pageToken=next_page_token
            ).execute()
            subscriptions.extend(response.get('items'))
            next_page_token = response.get('nextPageToken')
        return subscriptions
