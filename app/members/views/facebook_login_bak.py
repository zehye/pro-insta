import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect

User = get_user_model()

__all__ = (
    'facebook_login',
)


def facebook_login(request):
    # GET parameter의 'code'
    # request의 GET에 온 'code'값을 HttpResponse로 보여주기
    # 이 view와 urls를 연결(주소는 redireect_uri에 있는 주소)

    # 왼쪽 엑세스 코드 교환 엔드포인트에 HTTP GET요청 후,
    # 결과, response.text값을 HttpResponse에 출력

    def get_access_token(request):
        """
        Authorization code를 사용해 토큰을 받아옴
        :param request: 유저의 페이스북 인증 후 전달되는 Authorization code
        :return:
        """
        url = 'https://graph.facebook.com/v3.0/oauth/access_token'
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': 'http://localhost:8000/members/facebook-login/',
            'client_secret': settings.FACEBOOK_APP_SECRET_CODE,
            'code': code,
        }
        response = requests.get(url, params)
        # 파이선에 내장된 json모듈을 사용해서 , JSON형식의 텍스트를 파이썬 object로 변환
        # response_dict = json.loads(response.text)
        # 위와 같은 결과값을 가지고 옴
        response_dict = response.json()
        access_token = response_dict['access_token']

        return access_token

    # debug_token에 요청 보내고 결과 받기
    # 받은 결과의 'data'값을 HttpResponse로 출력
    #   input_token은 위의 'access_token'
    #   access_token은 {client_id} | {client_secret} 값

    def debug_token(request):
        """
        주어진 token을 Facebook의 debug_token API Endpoint를 사용해 검사
        :param request: 엑세스 토큰
        :return: JSON응답을 파싱한 파이썬 object
        """
        url = 'https://graph.facebook.com/debug_token'
        params = {
            'input_token': access_token,
            'access_token': '{}|{}'.format(
                settings.FACEBOOK_APP_ID,
                settings.FACEBOOK_APP_SECRET_CODE,
            )
        }
        response = requests.get(url, params)
        return response.json()

    # def get_user_info(token, fileds=None):

    def get_user_info(token, fields=('id', 'name', 'first_name', 'last_name', 'picture')):
        # 동적으로 params의 'fileds'값을 채울 수 있도록 매개변수 및 함수 내 동작 변경
        """
        주어진 token에 해당하는 Facebook User의 정보를 리턴
        :param request:
        :return:
        """
        # GraphAPI의 'me'(User) 이용해서 Facebook User정보 받아오기
        url = 'https://graph.facebook.com/v3.0/me'
        params = {
            'fields': ','.join(fields),
            # 'fields': 'id,name,first_name,last_name,picture',
            'access_token': token,
        }
        response = requests.get(url, params)
        response_dict = response.json()
        return response_dict

    def create_user_from_facebook_user_info(user_info):
        """
        Facebook Graph API의 'User'에 해당하는 응답인 user_info로부터
        id, first_name, last_name, picture항목을 사용해서
        Django의 User를 가져오거나 없는 경우 새로 만듬(get_or_create)
        :param user_info: Facebook GraphAPI - User의 응답
        :return: get_or_create의 결과 tuple (User instance, Bool(created)
        """
        # 받아온 정보 중 회원가입에 필요한 요소들 꺼내기
        facebook_user_id = user_info['id']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        url_img_profile = user_info['picture']['data']['url']

        # facebook_user_id가 username인 User를 기준으로 가져오거나 새로 생성
        return User.objects.get_or_create(
            username=facebook_user_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            },
        )

    # 유저가 새로 생성되었다면
    # get_or_create를 사용하지 않은 경우
    # if user_created:
    #     user.first_name = first_name
    #     user.last_name = last_name
    #     user.save()


    # return HttpResponse(response.text)

    code = request.GET['code']
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    user, user_create = create_user_from_facebook_user_info(user_info)

    login(request, user)
    return redirect('index')
