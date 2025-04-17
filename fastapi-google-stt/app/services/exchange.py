import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 한국수출입은행 환율 API 정보
API_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# 기본 환율 정보 (API 실패 시 사용)
DEFAULT_RATES = {
    "KRW": 1,
    "USD": 1421,
    "JPY": 10,
    "EUR": 1618,
    "CNY": 194,
    "LAK": 0.07,
}


def get_search_date() -> str:
    """
    오전 11시 이전이면 전날 날짜, 이후면 오늘 날짜 반환 (YYYYMMDD)
    주말인 경우 금요일 날짜 반환
    """
    now = datetime.now()
    if now.hour < 11:
        now -= timedelta(days=1)

    # 주말인 경우 금요일로 설정
    while now.weekday() > 4:  # 5는 토요일, 6은 일요일
        now -= timedelta(days=1)

    return now.strftime("%Y%m%d")


def is_100_unit_currency(cur_unit: str) -> bool:
    """100단위 통화인지 확인"""
    return "(100)" in cur_unit


def get_exchange_rate_safe(currency_code: str, search_date: str = None) -> float:
    """안전하게 환율 정보를 가져옵니다."""
    if currency_code == "KRW":
        return 1

    if not search_date:
        search_date = get_search_date()

    params = {
        "authkey": EXCHANGE_API_KEY,
        "searchdate": search_date,
        "data": "AP01",
    }

    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    try:
        logging.info(f"[환율 API 요청] 통화: {currency_code}, 날짜: {search_date}")
        response = requests.get(API_URL, params=params, headers=headers, timeout=5)
        logging.info(f"[환율 API 응답] 상태 코드: {response.status_code}")
        response.raise_for_status()
        exchange_data = response.json()
        logging.info(f"[환율 API 데이터] {exchange_data}")

        if not exchange_data:
            logging.warning(
                f"[환율 데이터 없음] {search_date} 날짜의 환율 정보가 없습니다."
            )
            # 이전 날짜로 재시도
            new_date = (
                datetime.strptime(search_date, "%Y%m%d") - timedelta(days=1)
            ).strftime("%Y%m%d")
            return get_exchange_rate_safe(currency_code, new_date)

        for item in exchange_data:
            cur_unit = item["cur_unit"].strip().upper()
            if currency_code.upper() in cur_unit:
                rate = float(item["deal_bas_r"].replace(",", ""))

                # JPY(100), IDR(100) 등 100단위 통화 처리
                if is_100_unit_currency(cur_unit):
                    rate = rate / 100

                logging.info(
                    f"[환율 조회 성공] {currency_code} = {float(rate)} KRW ({search_date})"
                )
                return float(rate)

        logging.warning(f"[환율 미존재] {currency_code}는 응답에 없음. 기본값 사용")
    except Exception as e:
        logging.warning(f"[환율 오류] {currency_code} 환율 조회 실패: {e}")

    fallback = float(DEFAULT_RATES.get(currency_code, 1))
    logging.info(f"[기본 환율 사용] {currency_code} = {fallback}")
    return fallback
