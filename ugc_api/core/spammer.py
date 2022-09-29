import datetime
import logging
import random
import uuid
from queue import Queue
from threading import Thread
from typing import List

import jwt
import requests
from models.body import Bookmark, FilmTimeStamp, LikeFilm, LikeFilmReview, MetaReview, Review

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ThreadPost(Thread):
    def __init__(self, queue, save_func):
        Thread.__init__(self)
        self.queue = queue
        self.save_func = save_func

    def run(self):
        while True:
            ti = self.queue.get()
            try:
                self.save_func(ti)
            finally:
                self.queue.task_done()


class UniqueGenerator:
    user_ids: set = set()
    film_ids: set = set()

    def __init__(
        self,
        n_users: int = 10000,
        n_films: int = 10000,
    ):
        self.n_users = n_users
        self.n_films = n_films

    def generate_user_id(self):
        while len(self.user_ids) < self.n_users:
            self.user_ids.add(uuid.uuid4())

    def generate_film_id(self):
        while len(self.film_ids) < self.n_films:
            self.film_ids.add(uuid.uuid4())

    def get_user_ids(self):
        return self.user_ids

    def get_film_ids(self):
        return self.film_ids

    def gen(self):
        self.generate_film_id()
        self.generate_user_id()


class BaseSpammer:
    def __init__(
        self,
        url: str,
        user_ids: set,
        film_ids: set,
        n_posts: int = 1000000,
        n_workers=10,
        jwt_secret: str = "qwerty",
    ):
        self.url = url
        self.n_posts = n_posts
        self.n_workers = n_workers
        self.jwt_secret = jwt_secret
        self.user_ids = user_ids
        self.film_ids = film_ids

    def _generate_element(self):
        raise NotImplementedError

    def data_generator(self):
        posts_now = 0
        while self.n_posts > posts_now:
            yield self._generate_element()
            if self.n_posts == -1:
                posts_now -= 1
            else:
                posts_now += 1

    def post(self, data):
        requests.post(url=self.url, data=data.json())

    def threading_post(self):
        queue = Queue()
        for _ in range(self.n_workers):
            worker = ThreadPost(queue, self.post)
            worker.daemon = True
            worker.start()
        return queue

    def spam(self, user_threads=False):
        if user_threads:
            queue = self.threading_post()
        for data in self.data_generator():
            if user_threads:
                queue.put(data)
            else:
                self.post(data)
        if user_threads:
            queue.join()
        logger.info("Complete")


class TimeStampSpammer(BaseSpammer):
    def _generate_element(self):
        return FilmTimeStamp(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            film_id=str(random.sample(self.film_ids, 1)[0]),
            film_timestamp=datetime.datetime.now(),
            event_time=datetime.datetime.now(),
        )


class FilmLikeSpammer(BaseSpammer):
    def _generate_element(self):
        return LikeFilm(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            film_id=str(random.sample(self.film_ids, 1)[0]),
            event_time=datetime.datetime.now(),
            score=random.random() * 10,
        )


class ReviewFilmLikeSpammer(BaseSpammer):
    def _generate_element(self):
        return LikeFilmReview(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            review_id=str(random.sample(self.film_ids, 1)[0]),
            event_time=datetime.datetime.now(),
            score=random.random() * 10,
        )


class BookmarksSpammer(BaseSpammer):
    def _generate_element(self):
        return Bookmark(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            film_id=str(random.sample(self.film_ids, 1)[0]),
            event_time=datetime.datetime.now(),
        )


class ReviewSpammer(BaseSpammer):
    def _generate_element(self):
        return Review(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            review_id=uuid.uuid4(),
            film_id=str(random.sample(self.film_ids, 1)[0]),
            event_time=datetime.datetime.now(),
            meta=MetaReview(author_id=str(random.sample(self.user_ids, 1)[0]), review_time=datetime.datetime.now()),
        )


class SpammerManager:
    def __init__(self, spammers: List[BaseSpammer]):
        self.spammers = spammers
        self.spammers_threads: List[Thread] = []

    def start(self):
        for sp in self.spammers:
            t_sp = Thread(target=sp.spam, kwargs={"user_threads": True})
            self.spammers_threads.append(t_sp)
            t_sp.start()

    def stop(self):
        for t_sp in self.spammers_threads:
            t_sp.join()


if __name__ == "__main__":
    ug = UniqueGenerator(n_films=1000, n_users=1000)
    ug.gen()
    rv_spammer = ReviewSpammer(
        url="http://localhost:8000/api/v1/review/film/",
        user_ids=ug.get_user_ids(),
        film_ids=ug.get_film_ids(),
        n_workers=10,
        n_posts=100,
    )
    bm_spammer = BookmarksSpammer(
        url="http://localhost:8000/api/v1/bookmarks/film/",
        user_ids=ug.get_user_ids(),
        film_ids=ug.get_film_ids(),
        n_workers=10,
        n_posts=100,
    )
    fl_spammer = FilmLikeSpammer(
        url="http://localhost:8000/api/v1/like/film/",
        user_ids=ug.get_user_ids(),
        film_ids=ug.get_film_ids(),
        n_workers=10,
        n_posts=100,
    )
    rvfl_spammer = ReviewFilmLikeSpammer(
        url="http://localhost:8000/api/v1/like/review/",
        user_ids=ug.get_user_ids(),
        film_ids=ug.get_film_ids(),
        n_workers=10,
        n_posts=100,
    )
    ts_spammer = TimeStampSpammer(
        url="http://localhost:8000/api/v1/films/film-timestamp/",
        user_ids=ug.get_user_ids(),
        film_ids=ug.get_film_ids(),
        n_workers=10,
        n_posts=100,
    )
    sm = SpammerManager([rv_spammer, bm_spammer, fl_spammer, rvfl_spammer, ts_spammer])
    sm.start()
    sm.stop()
