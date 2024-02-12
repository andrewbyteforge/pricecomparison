import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseNotAllowed
from database.models import Basket, BasketItem, Product

logger = logging.getLogger(__name__)

def index(request):
    """
    Render the index page.

    Args:
    request: HttpRequest object.

    Returns:
    HttpResponse object with rendered index page.
    """
    return render(request, 'index.html')

@login_required
@csrf_exempt
def add_to_basket(request):
    """
    Adds a product item to the user's basket.

    Args:
    request: HttpRequest object containing POST data with store, name, and price of the product.

    Returns:
    JsonResponse object with success status and added item information or error message.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            store, name, price = data['store'], data['name'], data['price']
            logger.info(f"Received data to add to basket: Store - {store}, Name - {name}, Price - {price}")
            data = json.loads(request.body)
            store = data['store'] 
            
            print("Received data:", data)

            # Retrieve or create the product and user's basket
            product, _ = Product.objects.get_or_create(store=store, name=name, defaults={'price': price})
            basket, _ = Basket.objects.get_or_create(user=request.user)

            # Add product to the basket
            basket_item = BasketItem.objects.create(basket=basket, product=product)            

            logger.info(f"Added item to basket: {basket_item.product.name}, ID: {basket_item.id}")
            print(f"Added to basket: {basket_item.product.name}, Quantity: {basket_item.quantity}")

            # Prepare and send response
            response_data = {
                "success": True, 
                "store": store, 
                "name": name, 
                "price": str(price), 
                "itemId": basket_item.id
            }
            return JsonResponse(response_data)
        except KeyError:
                return JsonResponse({'error': 'Missing store key'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            logger.error(f"Error in add_to_basket: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.warning("Invalid request method in add_to_basket")
        return JsonResponse({'error': 'Invalid request'}, status=400)


@require_POST
@login_required
@csrf_exempt
def remove_from_basket(request):
    """
    Removes a product item from the user's basket.

    Args:
    request: HttpRequest object containing POST data with the item's ID.

    Returns:
    JsonResponse object with success status or error message.
    """
    # Check if the request method is POST
    if request.method != 'POST':
        # Return a method not allowed response or a simple error message
        return HttpResponseNotAllowed(['POST'], "This endpoint only supports POST requests.")

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from request body.")
        return JsonResponse({"success": False, "error": "Invalid or missing JSON data"}, status=400)

    item_id = data.get('item_id')
    print(data)
    print(f'Item id of product: {item_id}')

    if not item_id:
        logger.error("No item ID provided in remove_from_basket")
        return JsonResponse({"success": False, "error": "No item ID provided"}, status=400)

    try:
        item = BasketItem.objects.get(id=item_id, basket__user=request.user)
        item.delete()
        logger.info(f"Removed item ID {item_id} from basket for user {request.user.username}")
        return JsonResponse({"success": True, "message": "Item removed successfully"})
    except BasketItem.DoesNotExist:
        logger.error(f"Item ID {item_id} not found in basket for user {request.user.username}")
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)
    except Exception as e:
        logger.exception("Unexpected error occurred in remove_from_basket")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
