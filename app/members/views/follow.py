__all__ =(
    'follow_toggle',
)


def follow_toggle(request):
    """
    * GET요청은 처리하지 않음
    * 로그인 된 상태에서만 작동

    POST요청일 때
        1. request.POST로 'user_pk'값을 전달받음
            pk가 user_pk인 User를 user에 할당
        2. request.user의
    :param request:
    :return:
    """
