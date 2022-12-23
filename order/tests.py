import json

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from product.models import Product
from user.models import User


class Tests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(username='buyer', password='buyer', role=User.Role.BUYER, deposit=1000)
        self.buyer_token = Token.objects.create(user=self.buyer)
        self.seller = User.objects.create_user(username='seller', password='seller', role=User.Role.SELLER)
        self.seller_token = Token.objects.create(user=self.seller)
        self.product1 = Product.objects.create(**{
            'product_name': 'Product1',
            'cost': 10,
            'amount_available': 10,
            'seller_id': self.seller
        })
        self.product2 = Product.objects.create(**{
            'product_name': 'Product2',
            'cost': 1000,
            'amount_available': 10,
            'seller_id': self.seller
        })

    def test_login(self):
        buyer_credentials = {
            'username': 'buyer',
            'password': 'buyer'
        }
        response = self.client.post(reverse('login'), data=buyer_credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)
        # print(response.content, response.status_code)
        self.assertEqual(response_json['token'], self.buyer_token.key)

    def test_add_product_with_buyer(self):
        product_data = {
            'product_name': 'Product',
            'cost': 10,
            'amount_available': 10
        }
        response = self.client.post(reverse('product_list'), data=product_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_add_product_bad_cost(self):
        product_data = {
            'product_name': 'Product',
            'cost': 13,
            'amount_available': 3
        }
        response = self.client.post(reverse('product_list'), data=product_data,
                                    HTTP_AUTHORIZATION='Token ' + self.seller_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_bad_amount(self):
        product_data = {
            'product_name': 'Product',
            'cost': 10,
            'amount_available': -3
        }
        response = self.client.post(reverse('product_list'), data=product_data,
                                    HTTP_AUTHORIZATION='Token ' + self.seller_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_good(self):
        product_data = {
            'product_name': 'Product',
            'cost': 10,
            'amount_available': 10
        }
        response = self.client.post(reverse('product_list'), data=product_data,
                                    HTTP_AUTHORIZATION='Token ' + self.seller_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_deposit_with_seller(self):
        deposit_data = {
            'amount': 100
        }
        response = self.client.post(reverse('user_deposit'), data=deposit_data,
                                    HTTP_AUTHORIZATION='Token ' + self.seller_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_deposit_bad_amount(self):
        deposit_data = {
            'amount': 99
        }
        response = self.client.post(reverse('user_deposit'), data=deposit_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_deposit_good(self):
        deposit_data = {
            'amount': 100
        }
        response = self.client.post(reverse('user_deposit'), data=deposit_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_buy_with_seller(self):
        order_data = {
            'product_id': self.product1.pk,
            'amount': 10
        }
        response = self.client.post(reverse('order'), data=order_data,
                                    HTTP_AUTHORIZATION='Token ' + self.seller_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_buy_low_stock(self):
        order_data = {
            'product_id': self.product1.pk,
            'amount': 100
        }
        response = self.client.post(reverse('order'), data=order_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_low_balance(self):
        order_data = {
            'product_id': self.product2.pk,
            'amount': 10
        }
        response = self.client.post(reverse('order'), data=order_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_product_doesnt_exist(self):
        order_data = {
            'product_id': 123456789,
            'amount': 10
        }
        response = self.client.post(reverse('order'), data=order_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_good(self):
        order_data = {
            'product_id': self.product1.pk,
            'amount': 5
        }
        self.assertEqual(self.buyer.deposit, 1000)
        self.assertEqual(self.product1.amount_available, 10)
        response = self.client.post(reverse('order'), data=order_data,
                                    HTTP_AUTHORIZATION='Token ' + self.buyer_token.key)
        # print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(response.content)  # balance = 1000, spent = 50, change = 950
        self.assertEqual(response_json['data']['change_in_coins'], [0, 0, 0, 1, 9])  # array of 5, 10, 20, 50 and 100 cent coins
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.deposit, 950)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.amount_available, 5)