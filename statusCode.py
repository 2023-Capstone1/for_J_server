"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
400 에러 - 잘못된 요청
서버에서 요청을 처리할 수 없는 잘못된 요청을 보낸 경우 발생합니다.
요청에 필요한 파라미터가 누락된 경우, 형식이 맞지 않는 경우, 권한이 없는 경우 등이 해당됩니다.
요청 내용을 다시 확인하고, 필요한 정보를 제공한 후에 재시도합니다.

401 에러 - 인증 실패
서버에서 해당 페이지에 대한 인증 실패가 발생한 경우입니다.
로그인 정보가 올바르지 않거나, 인증이 필요한 페이지에 인증 없이 접근한 경우에 해당됩니다.
로그인 정보를 확인하고, 인증이 필요한 경우 인증을 수행한 후 다시 시도합니다.

403 에러 - 접근 금지
서버에서 해당 페이지에 대한 권한이 없는 경우 발생합니다.
로그인하지 않았거나, 권한이 없는 사용자가 요청한 경우에 해당됩니다.
로그인하거나 권한을 요청한 후 다시 시도합니다.

404 에러 - 페이지를 찾을 수 없음
해당 URL에 대한 페이지가 존재하지 않는 경우 발생합니다.
해당 페이지가 삭제되었거나 URL이 잘못된 경우가 대표적입니다.
해당 페이지가 존재하는지 다시 확인하거나, URL이 올바른지 확인하면 됩니다.

408 에러 - 서버에서 클라이언트의 요청을 처리하는 데 너무 오랜 시간이 걸렸음

500 에러 - 서버 내부 오류
서버에서 발생한 내부적인 오류로 인해 요청을 처리할 수 없는 경우 발생합니다.
코드 버그, 서버 세팅 오류 등이 원인이 될 수 있습니다.
문제가 발생한 서버 로그를 확인하여, 오류가 발생한 부분을 찾아 수정해야 합니다.

502 에러 - 게이트웨이 오류
서버에서 게이트웨이로 요청을 보낼 때, 게이트웨이에서 서버로 전달할 수 없는 오류가 발생한 경우입니다.
인터넷 연결이 불안정한 경우, 서버에 문제가 생긴 경우 등이 해당됩니다.
네트워크 연결을 다시 확인하고, 문제가 지속될 경우 시간을 두고 다시 시도합니다.

503 에러 - 서버가 현재 요청을 처리할 수 없음

504 에러 - 서버가 게이트웨이 역할을 하는 다른 서버로부터 응답을 받지 못했음
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

success = {"SUCCESS": 200} # 정상적으로 완료

signup_mail_error = {"signup_mail_error": 400} # 회원가입시 이메일이 중복 될 때
device_NoneInfo_error = {"device_NotInfo_error": 400} # device 정보가 없을 때
signup_error = {"signup_error": 400} # 회원가입 창에서 미기입 된 값이 있을 때
id_duplication_error = {"id_duplication_error": 400} # 중복된 아이디가 있을 때
email_duplication_error = {"email_duplication_error": 400} # 중복된 이메일이 있을 때
certification_Number = {"certification_Number":400} # 인증번호가 안맞을 때

login_id_error = {"login_id_error": 401} # 로그인시 아이디가 안맞을 때
login_pw_error = {"login_pw_error": 401} # 로그인시 비밀번호가 안맞을 때
login_id_pw_error = {"login_id_pw_error": 401} # 로그인시 아이디, 비밀번호가 안맞을 때
no_exist_user = {"no_exsit_user" : 401}
not_id = {"not_id": 401} # 아이디가 없을 때
not_pw = {"not_pw": 401} # 비밀번호가 없을 때
not_id_pw = {"not_id_pw": 401} # 아이디 또는 비밀번호가 없을 때
not_name = {"not_name": 401} # 이름이 틀릴 때
not_email = {"not_email": 401} # 이메일이 없을 때
# 비밀번호 수정 에러
not_equal_new_pw = {"not_equal_new_pw": 401} # 비밀번호 변경할 때 새로운 비번 != 새로운 비번 체크

not_equal_id = {"not_equal_id": 401} # 로그인 아이디(str)와 유저 아이디(int, .id 값)가 다를 때

# 모든 list_id 에러
no_list_id = {"no_list_id": 401} # list_id 안넘겨줬을 때

# 투두API 에러
not_todo_name = {"not_todo_name": 401} # 투두 리스트 없을 때
not_todo_date = {"not_todo_date": 401} # 투두 날짜가 없을 때
not_todo_cName = {"not_todo_cName": 401} # 카테고리가 없을 때, 카테고리 오류
not_todo_state = {"not_todo_state": 401} # 상태가 없을 때 
no_exist_todo_list = {"no_exist_todo_list": 401} # 투두 리스트가 없을 때
none_correction_data = {"none_correction_data": 401} # 일치하는 정보가 없을 때
none_correction_cName_data = {"none_correction_cName_data": 401} # 일치하는 cName 정보가 없을 때
wrong_name = {"wrong_name": 401} # 투두 리스트 이름 오류
wrong_date = {"wrong_date": 401} # 투두 리스트 날짜 오류
same_todo_state = {"same_todo_state": 401} # 상태코드 그대로
no_list_id = {"no_list_id": 401} # 리스트 아이디가 없을 때

# 카테고리API 에러
no_isTodo = {"no_isTodo": 401} # isTodo 에러
no_todo_category = {"no_todo_category": 401} # 투두 카테고리가 없을 때
no_time_category = {"no_time_category": 401} # 타임 카테고리가 없을 때
no_category_color = {"no_category_color": 401} # 카테고리 색상 오류(없을 때)
no_category_name = {"no_category_name": 401} # 카테고리 이름 오류(없을 때)
no_category_name_color = {"no_category_name_color": 401} # 카테고리 이름이랑 색깔 둘 다 없을 때
isTodo_error = {"isTodo_error": 401} # isTodo 입력 오류(타임 찾는 곳에서 투두isTodo 입력 등)

# 타임트래커API 에러
no_exist_time_list = {"no_exist_time_list": 401} # 타임트래커 리스트가 존재하지 않을 때
no_time_name = {"no_time_name": 401} # 타임트래커 이름 없을 때
not_equal_time_name = {"not_equal_time_name": 401}
no_time_today = {"no_time_today": 401} # 타임트래커 오늘날짜 없을 때
no_time_cName = {"no_time_cName": 401} # 타임트래커 카테고리 이름 없을 때
no_time_nfc = {"no_time_nfc": 401} # 타임트래커 nfc 값 없을 때
no_time_order = {"no_time_order": 401} 
no_time_startTime = {"no_time_startTime": 401} 
no_time_endTime = {"no_time_endTime": 401} 
no_time_timeTaken = {"no_time_timeTaken": 401} 
no_exist_timeOrder_list = {"no_exist_timeOrder_list": 401} # 타임트래커 리스트가 존재하지 않을 때
no_exist_timeOrder_order = {"no_exist_timeOrder_order":401} # 타임트래커 오더가 없을 때

# 해빗API 에러
not_habit_list = {"not_habit_list": 401} # 해빗리스트 못 불러올 때
not_habit_name = {"not_habit_name": 401} 
not_habit_today = {"not_habit_today": 401} 
not_habit_startDate = {"not_habit_startDate": 401} 
not_habit_endDate = {"not_habit_endDate": 401} 
not_habit_alarmSwitch = {"not_habit_alarmSwitch": 401} 
not_habit_alarm = {"not_habit_alarm": 401} 
not_habit_repeatDay = {"not_habit_repeatDay": 401} 
not_habit_repeatN = {"not_habit_repeatN": 401} 
not_habit_habit_color = {"not_habit_habit_color": 401} 
not_habit_habit_nfc = {"not_habit_habit_nfc": 401}
not_habit_habit_state = {"not_habit_habit_state": 401} 
not_equal_name = {"not_equal_name": 401} # 리스트 이름 불일치
not_equal_today = {"not_equal_today": 401} # 리스트를 등록한 날짜가 맞지 않을 때
not_equal_startDate = {"not_equal_startDate": 401} # 리스트를 등록한 날짜가 맞지 않을 때
not_equal_endDate = {"not_equal_endDate": 401} # 리스트를 등록한 날짜가 맞지 않을 때

# 캘린더API 에러
no_cal_name = {"no_cal_name": 401} # 캘린더 이름 없을 때
no_cal_color = {"no_cal_color": 401} # 캘린더 색 없을 때
no_cal_allday = {"no_cal_allday": 401}
no_cal_startDate = {"no_cal_startDate": 401} # 캘린더 시작날짜 없을 때
no_cal_startTime = {"no_cal_startTime": 401} # 캘린더 시작시간 없을 때
no_cal_endDate = {"no_cal_endDate": 401} # 캘린더 종료날짜 없을 때
no_cal_endTime = {"no_cal_endTime": 401} # 캘리더 종료시간 없을 때
no_cal_location = {"no_cal_location": 401} # 캘린더 위치 없을 때
no_cal_alarm = {"no_cal_alarm": 401} # 캘린더 알람 없을 때
no_cal_alarmTime = {"no_cal_alarmTime": 401} # 캘린더 알람시간 없을 때
no_cal_memo = {"no_cal_memo": 401} # 캘린더 메모 없을 때
not_exist_cal_list = {"not_exist_cal_list": 401} # 캘린더 리스트 없을 때

unexpected_error = {"unexpected error": 401} # 예상치 못한 에러

url_error = {"url_error": 404} # Url 이 잘못됐을 때