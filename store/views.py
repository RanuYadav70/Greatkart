from django.shortcuts import render,get_object_or_404, redirect 
from .models import Product ,ReviewRating,ProductGallery
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from .forms import ReviewForm
from django.contrib import messages 
from orders.models import OrderProduct
# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        products= Product.objects.filter(category=categories,is_available=True)
        paginator = Paginator(products,3)
        page=request.GET.get('page')
        paged_products= paginator.get_page(page)
        product_count= products.count()
    else:  
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,3)
        page=request.GET.get('page')
        paged_products= paginator.get_page(page)
        product_count = products.count()

    context={
        'products': paged_products,
        'product_count':product_count,
    }
   
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug= category_slug, slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
       
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
    else:
        orderproduct = None


    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    # get a product 
    product_gallery  = ProductGallery.objects.filter(product_id=single_product.id)
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery,
    }

    return render(request,'store/product_detail.html',context)
def search(request):
    # Initialize products to an empty queryset or all products if no keyword is provided
    products = Product.objects.all()

    # Get the search keyword from the request
    keyword = request.GET.get('keyword2', '')

    # If a keyword is provided, filter the products by the correct field names
    if keyword:
        # Filter by product_name and description fields using Q objects for OR condition
        products = products.filter(
            Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
        )
        product_count = products.count()
    # Pass the products to the template
    return render(request, 'store/store.html', {
        'products': products,  # Ensure products is always defined
        'product_count':product_count,
    })

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')  # Get the referring URL to redirect back to

    if request.method == 'POST':
        # Use filter instead of get to avoid MultipleObjectsReturned error
        reviews = ReviewRating.objects.filter(user__id=request.user.id, product__id=product_id)

        if reviews.exists():  # If there are existing reviews
            review = reviews.first()  # Get the first review from the QuerySet
            form = ReviewForm(request.POST, instance=review)  # Pass the single instance to the form

            if form.is_valid():
                form.save()
                messages.success(request, "Thank you! Your review has been updated.")
        else:
            # No review exists for this user and product, create a new review
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.ip = request.META.get('REMOTE_ADDR')  # Save the user's IP address
                data.product_id = product_id  # Associate with the correct product
                data.user_id = request.user.id  # Associate with the logged-in user
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
        
        return redirect(url)