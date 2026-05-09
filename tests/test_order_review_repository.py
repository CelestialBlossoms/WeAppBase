import datetime as dt
import importlib

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def order_review_module():
    app = Flask(__name__)
    app.config['DATABASE_TYPE'] = 'mysql'
    with app.app_context():
        yield importlib.import_module('backend.mini_core.repository.order.order_review')


@pytest.fixture
def order_review_repo(order_review_module):
    engine = create_engine('sqlite:///:memory:')
    order_review_module.order_review_table.create(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = order_review_module.OrderReviewSQLARepository(session)
    try:
        yield repo, session, order_review_module.OrderReview
    finally:
        session.close()
        engine.dispose()


def _review(model, review_id, **kwargs):
    data = {
        'order_no': 'order-1',
        'order_detail_id': f'detail-{review_id}',
        'product_id': 100,
        'user_id': 'user-1',
        'nickname': 'tester',
        'rating': 5,
        'content': 'ok',
        'images': None,
        'is_anonymous': False,
        'status': '\u5df2\u53d1\u5e03',
        'is_top': False,
        'review_time': dt.datetime(2026, 5, 9, 12, 0, review_id),
    }
    data.update(kwargs)
    review = model(**data)
    review.id = review_id
    return review


def test_product_user_and_order_reviews_only_return_published(order_review_repo):
    repo, session, model = order_review_repo
    session.add_all([
        _review(model, 1, rating=5, images='["a.jpg"]'),
        _review(model, 2, rating=1, status='\u5ba1\u6838\u4e2d', images='["hidden.jpg"]'),
    ])
    session.commit()

    product_reviews, total = repo.get_product_reviews(100, need_total_count=True)
    user_reviews = repo.get_user_reviews('user-1')
    order_reviews = repo.get_order_reviews('order-1')
    override_reviews, override_total = repo.get_product_reviews(
        100,
        status='\u5ba1\u6838\u4e2d',
        need_total_count=True,
    )

    assert total == 1
    assert [review.id for review in product_reviews] == [1]
    assert [review.id for review in user_reviews] == [1]
    assert [review.id for review in order_reviews] == [1]
    assert override_total == 1
    assert [review.id for review in override_reviews] == [1]


def test_reviews_with_images_ignores_empty_image_values(order_review_repo):
    repo, session, model = order_review_repo
    empty_images = [None, '', '   ', '[]', ' [ ] ', '[""]', '[null]']
    session.add_all([
        _review(model, index + 1, product_id=200, images=image_value)
        for index, image_value in enumerate(empty_images)
    ])
    session.add(_review(model, 20, product_id=200, images='["real.jpg"]'))
    session.commit()

    reviews, total = repo.get_reviews_with_images(200, need_total_count=True)
    stats = repo.get_review_count_by_rating(200)

    assert total == 1
    assert [review.id for review in reviews] == [20]
    assert stats['with_images'] == 1


def test_review_statistics_only_count_published_reviews(order_review_repo):
    repo, session, model = order_review_repo
    session.add_all([
        _review(model, 1, product_id=300, rating=5, images='["a.jpg"]'),
        _review(model, 2, product_id=300, rating=3, images='[]'),
        _review(model, 3, product_id=300, rating=1, status='\u5ba1\u6838\u4e2d', images='["hidden.jpg"]'),
    ])
    session.commit()

    stats = repo.get_review_count_by_rating(300)

    assert stats['total'] == 2
    assert stats['rating_5'] == 1
    assert stats['rating_3'] == 1
    assert stats['rating_1'] == 0
    assert stats['good'] == 1
    assert stats['mid'] == 1
    assert stats['bad'] == 0
    assert stats['with_images'] == 1
    assert stats['avg_rating'] == 4.0
    assert stats['rating_detail'][4] == {'rating': 5, 'count': 1, 'percentage': 50.0}


def test_review_statistics_for_no_reviews_returns_zeroes(order_review_repo):
    repo, _, _ = order_review_repo

    stats = repo.get_review_count_by_rating(999)

    assert stats['total'] == 0
    assert stats['with_images'] == 0
    assert stats['avg_rating'] == 0.0
    assert all(stats[f'rating_{rating}'] == 0 for rating in range(1, 6))
    assert all(item['percentage'] == 0.0 for item in stats['rating_detail'])
