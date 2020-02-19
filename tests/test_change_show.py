import os
import unittest

import NotAOrm
from NotAOrm.datatype import Int, Varchar
from NotAOrm.table import Table

NotAOrm.database = 'test.db'


class TestChange(unittest.TestCase):
    site = Table(table_name='site', table_row=(
        Int('id', primary_key=True),
        Varchar('url', length=255),
        Int('visitor')
    ))

    @classmethod
    def setUpClass(cls):
        cls.site.change._conn.execute("""
            create table site(id integer constraint site_pk primary key autoincrement, visitor integer DEFAULT 0, url TEXT not null); 
        """)

    def setUp(self):
        self.site.change._conn.executescript("""
            DELETE FROM site;
            insert into site ('url', 'visitor') values ('test.com', 10);
            insert into site ('url', 'visitor') values ('google.com', 1000);
            insert into site ('url', 'visitor') values ('google2.com', 100);
            insert into site ('url', 'visitor') values ('aaa.com', 15);
            insert into site ('url', 'visitor') values ('aaa.com', 5);
            insert into site ('url', 'visitor') values ('bbb.com', 5);
        """)
        self.site.change._conn.commit()

    def test_all(self):
        self.assertIsNotNone(self.site.show.all())

    def test_get(self):
        test_url = self.site.show.get(self.site.url == 'test.com')
        self.assertEqual(test_url.url, 'test.com')

    def test_get_conditional_and(self):
        conditions = (self.site.url == 'aaa.com') & (self.site.visitor == 5) & (self.site.id >= 0)
        site = self.site.show.get(conditions)
        self.assertEqual(site.url, 'aaa.com')
        self.assertEqual(site.visitor, 5)

    def test_get_conditional_or(self):
        conditions = (self.site.url == 'google.com') | (self.site.visitor == 5)
        sites = self.site.show.filter(conditions)
        self.assertEqual(len(list(sites)), 3)

    def test_insert(self):
        self.site.change.insert(url='facebook.com')
        self.assertIsNotNone(self.site.show.get(self.site.url == 'facebook.com'))

    def test_filter(self):
        test_url = self.site.show.filter(self.site.id >= 0)
        self.assertGreater(len(list(test_url)), 1)

    def test_update(self):
        self.site.change.update(self.site.url.is_like('test.c%'), url='test2.com')
        self.assertIsNone(self.site.show.get(self.site.url == 'test.com'))
        self.assertIsNotNone(self.site.show.get(self.site.url == 'test2.com'))

    def test_delete(self):
        self.site.change.delete(self.site.url == 'test.com', commit=True)
        self.assertIsNone(self.site.show.get(self.site.url == 'test.com'))

    def test_order_by(self):
        latest = self.site.show.filter(self.site.visitor == 5, order_by=self.site.id)
        self.assertEqual(list(latest)[0].url, 'aaa.com')

        first = self.site.show.filter(self.site.visitor == 5, order_by_desc=self.site.id)
        self.assertEqual(list(first)[0].url, 'bbb.com')

    def test_limit(self):
        last = self.site.show.all(limit=1)
        self.assertEqual(len(list(last)), 1)

    def test_group_by(self):
        site = self.site.show.get(
            self.site.url == 'aaa.com',
            self.site.visitor.sum,
            group_by=self.site.url
        )
        self.assertEqual(site.sum_visitor, 20)

        site = self.site.show.get(
            self.site.url == 'aaa.com',
            self.site.visitor.count,
            group_by=self.site.url
        )

        self.assertEqual(site.count_visitor, 2)

    def test_pk(self):
        site = self.site.show.get(self.site.pk == 1)
        self.assertEqual(site.id, 1)

    def test_first(self):
        self.assertEqual(self.site.show.first().url, 'test.com')

    def test_last(self):
        self.assertEqual(self.site.show.last().url, 'bbb.com')

    @classmethod
    def tearDownClass(cls):
        os.remove(NotAOrm.database)