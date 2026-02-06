import boto3
from config import Config
from botocore.exceptions import ClientError
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

class MockTable:
    def __init__(self):
        self.items = []
        print("Initialized MOCK DynamoDB Table")

    def put_item(self, Item, ConditionExpression=None):
        # check condition if needed (simplified)
        for i, existing in enumerate(self.items):
            if existing['PK'] == Item['PK'] and existing['SK'] == Item['SK']:
                if ConditionExpression == 'attribute_not_exists(PK)':
                     raise ClientError({'Error': {'Code': 'ConditionalCheckFailedException'}}, 'put_item')
                self.items[i] = Item
                return
        self.items.append(Item)

    def get_item(self, Key):
        for item in self.items:
            if item['PK'] == Key['PK'] and item['SK'] == Key['SK']:
                return {'Item': item}
        return {}

    def delete_item(self, Key):
        self.items = [i for i in self.items if not (i['PK'] == Key['PK'] and i['SK'] == Key['SK'])]

    def query(self, KeyConditionExpression):
        # Very basic mock query - matching PK exactly
        # This relies on the fact that existing code passes boto3 conditions which are objects.
        # We need a simpler way to filter for the mock or parse the expression effectively.
        # For this specific app, we know the queries are:
        # PK=... and SK begins_with(...)
        
        # We'll rely on a manual filter method or simply return all items for the user 
        # since we can't easily parse boto3 KeyConditionExpression objects here without logic.
        # ALTERNATIVE: Hack the calls in the Database methods to use a helper.
        pass 
        # See Database methods update below - we will handle logic there.

    def scan(self, FilterExpression=None, Select=None):
        if Select == 'COUNT':
            return {'Count': len(self.items)}
        return {'Items': self.items}

class Database:
    _mock_data = [] # Shared static mock data storage to persist across requests in single process dev server

    def __init__(self):
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.table_name = Config.DYNAMODB_TABLE_NAME
            self.table = self.dynamodb.Table(self.table_name)
            # Test connection
            self.table.load()
            self.is_mock = False
        except (ClientError, boto3.exceptions.Boto3Error, Exception) as e:
            print(f"AWS Connection Failed: {e}. Switching to MOCK Database.")
            self.is_mock = True
            self.table = MockTable()
            self.table.items = Database._mock_data
    
    def create_user(self, username, email, password):
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        
        # Auto-admin logic for mock mode (Secure: only specific email)
        role = 'user'
        if self.is_mock and email == 'admin@stocker.com':
            role = 'admin'
            print(f"Assigning ADMIN role to: {email}")

        try:
            # We use a composite key approach or simple PK depending on table design.
            # Assuming Single Table Design or simple per-entity table. 
            # For simplicity in this demo, we'll store everything in one table with PK 'PK' and SK 'SK'.
            # PK: USER#<email>, SK: PROFILE
            
            response = self.table.put_item(
                Item={
                    'PK': f"USER#{email}",
                    'SK': 'PROFILE',
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'password': hashed_password,
                    'role': role,
                    'created_at': int(time.time())
                },
                ConditionExpression='attribute_not_exists(PK)'
            )
            return True, user_id
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False, "User already exists"
            return False, str(e)

    def get_user(self, email):
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{email}",
                    'SK': 'PROFILE'
                }
            )
            return response.get('Item')
        except ClientError as e:
            print(e)
            return None

    def verify_password(self, email, password):
        user = self.get_user(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    def create_transaction(self, user_email, stock_symbol, action, quantity, price):
        transaction_id = str(uuid.uuid4())
        timestamp = int(time.time())
        try:
            self.table.put_item(
                Item={
                    'PK': f"USER#{user_email}",
                    'SK': f"TX#{timestamp}#{transaction_id}",
                    'transaction_id': transaction_id,
                    'stock_symbol': stock_symbol,
                    'action': action, # BUY or SELL
                    'quantity': quantity,
                    'price': str(price),
                    'total': str(float(price) * int(quantity)),
                    'timestamp': timestamp
                }
            )
            # Update Portfolio (Simplified: Fetch, Update, Put)
            self.update_portfolio(user_email, stock_symbol, action, quantity, price)
            return True, transaction_id
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return False, str(e)

    def update_portfolio(self, user_email, stock_symbol, action, quantity, price):
        # This is a simplification. In a real app we'd use DynamoDB Atomic Counters or Transactions.
        # Fetch current holding
        pk = f"USER#{user_email}"
        sk = f"HOLDING#{stock_symbol}"
        
        try:
            response = self.table.get_item(Key={'PK': pk, 'SK': sk})
            item = response.get('Item')
            
            current_qty = int(item['quantity']) if item else 0
            
            new_qty = current_qty
            if action == 'BUY':
                new_qty += int(quantity)
            elif action == 'SELL':
                new_qty -= int(quantity)
            
            if new_qty < 0:
                raise ValueError("Insufficient holdings")
                
            if new_qty == 0 and item:
                self.table.delete_item(Key={'PK': pk, 'SK': sk})
            else:
                self.table.put_item(
                    Item={
                        'PK': pk,
                        'SK': sk,
                        'symbol': stock_symbol,
                        'quantity': new_qty,
                        'updated_at': int(time.time())
                    }
                )
        except Exception as e:
            print(f"Portfolio update failed: {e}")
            raise e

    def get_portfolio(self, user_email):
        try:
            if self.is_mock:
                # Mock Query Logic: filter by PK=USER#email and SK stars with HOLDING#
                items = [i for i in self.table.items if i.get('PK') == f"USER#{user_email}" and i.get('SK', '').startswith('HOLDING#')]
                return items
            
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(f"USER#{user_email}") & boto3.dynamodb.conditions.Key('SK').begins_with('HOLDING#')
            )
            return response.get('Items', [])
        except ClientError as e:
            print(e)
            return []

    def get_transactions(self, user_email):
        try:
            if self.is_mock:
                # Mock Query Logic: filter by PK=USER#email and SK stars with TX#
                items = [i for i in self.table.items if i.get('PK') == f"USER#{user_email}" and i.get('SK', '').startswith('TX#')]
                return items
                
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(f"USER#{user_email}") & boto3.dynamodb.conditions.Key('SK').begins_with('TX#')
            )
            return response.get('Items', [])
        except ClientError as e:
            print(e)
            return []

    def get_all_users(self):
        try:
            if self.is_mock:
                return [i for i in self.table.items if i.get('SK') == 'PROFILE']

            # Scan is expensive, but for a simple/small app admin view it's acceptable.
            # In production with many users, we would use a GSI (Global Secondary Index) on ROLE.
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('PROFILE')
            )
            return response.get('Items', [])
        except ClientError as e:
            print(e)
            return []

    def get_system_stats(self):
        try:
            # Scan to count everything - not efficient for large scale but fine here
            users = self.get_all_users()
            user_count = len(users)
            
            if self.is_mock:
                total_items = len(self.table.items)
            else:
                # Simple count of all items roughly
                response = self.table.scan(Select='COUNT')
                total_items = response['Count']
            
            return {
                'total_users': user_count,
                'total_items': total_items,
                'status': 'Healthy' # Mock status
            }
        except ClientError as e:
            print(e)
            return {'error': str(e)}

    def create_stock(self, symbol, name, initial_price):
        try:
            # PK: STOCK#<symbol>, SK: META
            item = {
                'PK': f"STOCK#{symbol}",
                'SK': 'META',
                'symbol': symbol,
                'name': name,
                'current_price': str(initial_price),
                'created_at': int(time.time())
            }
            
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return True, symbol
        except ClientError as e:
            print(f"Error creating stock: {e}")
            return False, str(e)

    def get_all_stocks(self):
        try:
            if self.is_mock:
                return [i for i in self.table.items if i.get('PK', '').startswith('STOCK#') and i.get('SK') == 'META']

            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('PK').begins_with('STOCK#') & boto3.dynamodb.conditions.Attr('SK').eq('META')
            )
            return response.get('Items', [])
        except ClientError as e:
            print(e)
            return []
