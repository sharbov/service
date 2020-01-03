# coding: utf-8
from __future__ import absolute_import

import datetime

import mock
from flask import json

from service.orm.database import db
from service.orm.item import Item, Status
from tests.ut.base import BaseTestCase


class TestItemAPI(BaseTestCase):
    """Item API tests."""

    def test_create_item_happy_flow(self):
        """Test create_item - happy flow."""
        test_name = "test-name"

        response = self.client.open(
            "/service/api/v1/item",
            method="POST",
            data=json.dumps({"name": test_name}),
            content_type="application/json",
        )
        self.assertStatus(
            response,
            201,
            "Response body is : " + response.data.decode("utf-8"),
        )

        created_item = response.json

        # Validate the response data
        self.assertEqual(created_item["name"], test_name)
        self.assertIn("created_at", created_item)
        self.assertIn("updated_at", created_item)

    def test_create_item_bad_request(self):
        """Test create_item - bad requests."""
        cases = [
            {"name": ""},  # empty name
            {"name": "*" * 100},  # name too long
        ]
        for create_item_case in cases:
            response = self.client.open(
                "/service/api/v1/item",
                method="POST",
                data=json.dumps(create_item_case),
                content_type="application/json",
            )
            self.assert400(
                response, "Response body is : " + response.data.decode("utf-8")
            )

    def test_worker_cpu_task_failure(self):
        """Test create_item - worker cpu-task failure."""
        with mock.patch(
            "service.managers.item.update_item", side_effect=[Exception, None]
        ) as mock_update:
            with self.assertRaises(Exception):
                self.client.open(
                    "/service/api/v1/item",
                    method="POST",
                    data=json.dumps({"name": "cpu-task-failure"}),
                    content_type="application/json",
                )

        # Validate the expected calls were made
        mock_update.assert_has_calls(
            [
                mock.call(item_id=mock.ANY, status="in-progress"),
                mock.call(item_id=mock.ANY, status="error"),
            ]
        )

    def test_worker_io_task_failure(self):
        """Test create_item - worker io-task failure."""
        with mock.patch(
            "service.managers.item.update_item",
            side_effect=[None, Exception, None],
        ) as mock_update:
            with self.assertRaises(Exception):
                self.client.open(
                    "/service/api/v1/item",
                    method="POST",
                    data=json.dumps({"name": "io-task-failure"}),
                    content_type="application/json",
                )

        # Validate the expected calls were made
        mock_update.assert_has_calls(
            [
                mock.call(item_id=mock.ANY, status="in-progress"),
                mock.call(item_id=mock.ANY, status="ready"),
                mock.call(item_id=mock.ANY, status="error"),
            ]
        )

    def test_get_item_not_found(self):
        """Test get_item - not found."""

        # Try getting a non-existent item
        response = self.client.open(
            "/service/api/v1/item/not-found-id",
            method="GET",
            content_type="application/json",
        )
        self.assert404(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_get_item_happy_flow(self):
        """Test get_item - happy flow."""
        test_id = "test-id"
        test_name = "test-name"

        test_updated_at = test_created_at = datetime.datetime.utcnow()

        mock_item = Item(
            id=test_id,
            name=test_name,
            status=Status.PENDING,
            created_at=test_created_at,
            updated_at=test_updated_at,
        )

        # Patch the users DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.filter.return_value.one_or_none.return_value = mock_item
            response = self.client.open(
                f"/service/api/v1/item/{test_id}",
                method="GET",
                content_type="application/json",
            )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

        get_item = response.json

        # Validate the response data
        self.assertEqual(get_item["name"], test_name)
        self.assertEqual(get_item["created_at"], get_item["updated_at"])

    def test_list_item(self):
        """Test list_item."""
        # Patch the item DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.order_by.return_value.paginate.return_value.items = []

            response = self.client.open(
                "/service/api/v1/item",
                method="GET",
                content_type="application/json",
                query_string={"status": Status.READY},
            )

        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

        item_list = response.json
        self.assertEqual(item_list, [])

        test_item = Item(
            id="ae18c3ef-0b32-44c0-9da3-d51c1c8c19e7",
            name="test-item",
            status=Status.IN_PROGRESS,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )

        # Patch the item DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.order_by.return_value.paginate.return_value.items = [
                test_item
            ]
            response = self.client.open(
                "/service/api/v1/item",
                method="GET",
                content_type="application/json",
            )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

        item_list = response.json

        # Validate the response data
        self.assertEqual(len(item_list), 1)
        self.assertEqual(item_list[0]["name"], test_item.name)

    def test_update_item_not_found(self):
        """Test update_item - not found."""
        response = self.client.open(
            "/service/api/v1/item/not-found-id",
            method="PUT",
            data=json.dumps({"name": "test_name"}),
            content_type="application/json",
        )
        self.assert404(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_update_item_bad_request(self):
        """Test update_item - bad requests."""
        cases = [
            {"name": ""},  # empty name
            {"name": "*" * 100},  # name too long
        ]
        # Patch the item DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.get_or_404.return_value = Item(id="test-id")
            for update_item_case in cases:
                response = self.client.open(
                    "/service/api/v1/item/test-id",
                    method="PUT",
                    data=json.dumps(update_item_case),
                    content_type="application/json",
                )
                self.assert400(
                    response,
                    "Response body is : " + response.data.decode("utf-8"),
                )

    def test_update_item_happy_flow(self):
        """Test update_item - happy flow."""
        test_id = "test-id"
        test_name = "test-name"

        # Patch the users DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.filter.return_value.one_or_none.return_value = Item(
                id=test_id,
                name="old-name",
                status=Status.READY,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            response = self.client.open(
                f"/service/api/v1/item/{test_id}",
                method="PUT",
                data=json.dumps({"name": test_name}),
                content_type="application/json",
            )

        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

        update_item = response.json

        # Validate the response data
        self.assertEqual(update_item["name"], test_name)

    def test_delete_item_not_found(self):
        """Test delete_item - not found."""
        response = self.client.open(
            "/service/api/v1/item/not-found-id",
            method="DELETE",
            content_type="application/json",
        )
        self.assert404(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_delete_item_happy_flow(self):
        """Test delete_item - happy flow."""
        test_item = Item()

        # Patch the item DB
        with mock.patch.object(Item, "query") as mock_query:
            mock_query.get_or_404.return_value = test_item
            with mock.patch.object(db, "session") as mock_session:
                response = self.client.open(
                    "/service/api/v1/item/test-id",
                    method="DELETE",
                    content_type="application/json",
                )
                mock_session.has_calls(
                    mock.call.delete(test_item), mock.call.commit()
                )
                self.assertStatus(response, 204)
