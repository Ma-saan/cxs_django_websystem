from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Material, Product, BOM

def index(request):
    product_count = Product.objects.count()
    material_count = Material.objects.count()
    bom_count = BOM.objects.count()
    context = {
        'product_count': product_count,
        'material_count': material_count,
        'bom_count': bom_count,
    }
    return render(request, 'inventory/index.html', context)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    bom_items = BOM.objects.filter(product=product)
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'bom_items': bom_items
    })

def material_list(request):
    materials = Material.objects.all()
    return render(request, 'inventory/material_list.html', {'materials': materials})

def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    bom_items = BOM.objects.filter(material=material)
    return render(request, 'inventory/material_detail.html', {
        'material': material,
        'bom_items': bom_items
    })

def bom_list(request):
    bom_items = BOM.objects.all()
    return render(request, 'inventory/bom_list.html', {'bom_items': bom_items})

def product_bom(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    bom_items = BOM.objects.filter(product=product)
    return render(request, 'inventory/product_bom.html', {
        'product': product,
        'bom_items': bom_items
    })