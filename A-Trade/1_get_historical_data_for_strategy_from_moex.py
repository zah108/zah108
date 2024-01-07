"""
    В этом коде мы асинхронно получаем исторические данные с MOEX
    и сохраняем их в CSV файлы. Т.к. получаем их бесплатно, то
    есть задержка в полученных данных на 15 минут.
    Автор: Олег Шпагин
    Github: https://github.com/WISEPLAT
    Telegram: https://t.me/OlegSh777
"""

from my_config.trade_config import Config  # Файл конфигурации торгового робота
from datetime import datetime, timedelta
import pandas as pd
import os
import functions
import aiomoex
import aiohttp
import asyncio
# exit(777)  # для запрета запуска кода, иначе перепишет результаты


async def get_candles(session, ticker, timeframes, start, end):
    """Функция получения свечей с MOEX."""
    for timeframe in timeframes:
        tf = functions.get_timeframe_moex(timeframe)
        # M10
        data = await aiomoex.get_market_candles(session, ticker, interval=tf, start=start, end=end)
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(
            df['begin'], format='%Y-%m-%d %H:%M:%S')
        # для M1, M10, H1 - приводим дату свечи в правильный вид
        if tf in [1, 10, 60]:
            df['datetime'] = df['datetime'].apply(
                lambda x: x + timedelta(minutes=tf))
        df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
        df.to_csv(os.path.join(
            "Data", f"{ticker}_{timeframe}.csv"), index=False, encoding='utf-8', sep=',')
        print(f"{ticker} {tf}:")
        print(df)


async def get_all_historical_candles(portfolio, timeframes, start, end):
    """Запуск асинхронной задачи получения исторических данных для каждого тикера из портфеля."""
    async with aiohttp.ClientSession() as session:
        strategy_tasks = []
        for instrument in portfolio:
            strategy_tasks.append(asyncio.create_task(
                get_candles(session, instrument, timeframes, start, end)))
        await asyncio.gather(*strategy_tasks)


if __name__ == "__main__":

    # применение настроек из config.py
    """
    Список тикеров в конфиге my_config/trade_config.py
    Два таймфрейма
    Загрузка с указанной даты по сейчас
    """
    portfolio = Config.portfolio  # тикеры по которым скачиваем исторические данные
    timeframe_0 = Config.timeframe_0  # таймфрейм для обучения нейросети - вход
    timeframe_1 = Config.timeframe_1  # таймфрейм для обучения нейросети - выход
    start = Config.start  # с какой даты загружаем исторические данные с MOEX
    end = datetime.now().strftime("%Y-%m-%d")  # по сегодня

    # создаем необходимые каталоги
    functions.create_some_folders(timeframes=[timeframe_0, timeframe_1])

    # запуск асинхронного цикла получения исторических данных
    loop = asyncio.get_event_loop()  # создаем цикл
    task = loop.create_task(  # в цикл добавляем 1 задачу
        get_all_historical_candles(  # запуск получения исторических данных с MOEX
            portfolio=portfolio,
            # по каким таймфреймам скачиваем данные
            timeframes=[timeframe_0, timeframe_1],
            start=start,
            end=end,
        )
    )
    loop.run_until_complete(task)  # ждем окончания выполнения цикла
