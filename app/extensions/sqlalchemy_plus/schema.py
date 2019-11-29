# -*- coding:utf-8 -*-
from marshmallow import Schema, fields


class _PageContent:
    def __init__(self, page, items):
        self.page = page
        self.items = items


class MobilePaginator:
    def __init__(self, query, page=1, per_page=10):
        page = int(page or 1)
        per_page = int(per_page or 10)
        self.page = 1 if page < 1 else page
        per_page = 10 if per_page < 1 else per_page
        self.per_page = 50 if per_page > 50 else per_page
        self.query = query
        self.page_query = query.limit(self.per_page).offset((self.page - 1) * self.per_page)

    def render_page(self):
        mobile_page = MobilePage()

        total = self.query.count()
        pages = divmod(total, self.per_page)
        total_pages = pages[0] + 1 if pages[1] else pages[0]

        mobile_page.has_next = self.page < total_pages
        mobile_page.page = self.page
        mobile_page.per_page = self.per_page

        return _PageContent(mobile_page, self.page_query.all())


class MobilePage:
    def __init__(self):
        self.page = 0
        self.per_page = 0
        self.has_next = False


class MobilePageSchema(Schema):
    page = fields.Integer()
    perPage = fields.Integer(attribute='per_page')
    hasNext = fields.Boolean(attribute='has_next')


class Paginator(object):
    def __init__(self, query, page=1, per_page=20):
        page = int(page)
        per_page = int(per_page)
        if page < 1 or page is None:
            page = 1
        if per_page < 1 or per_page is None:
            per_page = 20
        if per_page > 200:
            per_page = 200

        self._query = query
        self._page_query = query.limit(per_page).offset((page - 1) * per_page)
        self._page = page
        self._per_page = per_page

    @classmethod
    def _build_pages(cls, page):
        if page.current_page > 0:
            if page.total_pages > 10:
                if page.current_page > 4:
                    if page.current_page + 5 <= page.total_pages:
                        start = page.current_page - 4
                        end = page.current_page + 5 + 1
                    else:
                        start = page.total_pages - 9
                        end = page.total_pages + 1
                else:
                    start = 1
                    end = 10 + 1
            else:
                start = 1
                end = page.total_pages + 1

            for i in range(start, end):
                page.pages.append(i)

    def render_page(self):
        page = Page()
        page.total = self._query.count()

        pages = divmod(page.total, self._per_page)
        page.total_pages = pages[0] + 1 if pages[1] else pages[0]

        page.has_prev = self._page > 1
        page.prev_page = self._page - 1 if self._page > 1 else 0

        page.has_next = self._page < page.total_pages
        page.next_page = self._page + 1 if self._page < page.total_pages else 0

        page.first_page = 1 if page.total_pages > 0 else 0
        page.last_page = page.total_pages if page.total_pages > 0 else 0

        page.page_count = self._page_query.count()

        page.current_page = self._page if page.total_pages else 0
        page.per_page = self._per_page

        self._build_pages(page)
        # page 不是一个页码数字, 而是一个对象
        return _PageContent(page, self._page_query.all())


class Page(object):
    def __init__(self):
        self.total = 0
        self.total_pages = 0
        self.has_prev = False
        self.prev_page = 0
        self.has_next = False
        self.next_page = 0
        self.first_page = 0
        self.last_page = 0
        self.page_count = 0
        self.current_page = 0
        self.per_page = 0
        self.pages = []


class PageSchema(Schema):
    total = fields.Int(attribute='total')
    totalPages = fields.Int(attribute='total_pages')
    hasPrev = fields.Boolean(attribute='has_prev')
    prevPage = fields.Int(attribute='prev_page')
    hasNext = fields.Boolean(attribute='has_next')
    nextPage = fields.Int(attribute='next_page')

    firstPage = fields.Int(attribute='first_page')
    lastPage = fields.Int(attribute='last_page')

    pageCount = fields.Int(attribute='page_count')
    currentPage = fields.Int(attribute='current_page')
    perPage = fields.Int(attribute='per_page')
    pages = fields.List(fields.Int(), attribute='pages')
