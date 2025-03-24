from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Material, Product, BOM
from .forms import ProductForm, MaterialForm

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
    # 全ての製品を取得
    products = Product.objects.all()
    
    # ラインのリストを取得（重複なし）
    production_lines = Product.objects.values_list('production_line', flat=True).distinct().order_by('production_line')
    
    # GETパラメータからラインフィルタを取得
    line_filter = request.GET.get('line', '')
    
    # ラインでフィルタリング
    if line_filter:
        products = products.filter(production_line=line_filter)
    
    context = {
        'products': products,
        'production_lines': production_lines,
        'current_line': line_filter
    }
    
    return render(request, 'inventory/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    bom_items = BOM.objects.filter(product=product)
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'bom_items': bom_items
    })

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '製品が正常に追加されました。')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': '製品の追加'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '製品が正常に更新されました。')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'product': product, 'title': '製品の編集'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, '製品が削除されました。')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

def material_list(request):
    # すべての材料を取得
    materials = Material.objects.all()
    
    # キーワード検索
    search_query = request.GET.get('search', '')
    if search_query:
        materials = materials.filter(
            material_id__icontains=search_query
        ) | materials.filter(
            material_name__icontains=search_query
        )
    
    return render(request, 'inventory/material_list.html', {
        'materials': materials,
        'search_query': search_query
    })

def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    bom_items = BOM.objects.filter(material=material)
    return render(request, 'inventory/material_detail.html', {
        'material': material,
        'bom_items': bom_items
    })

def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '材料が正常に追加されました。')
            return redirect('inventory:material_list')
    else:
        form = MaterialForm()
    return render(request, 'inventory/material_form.html', {'form': form, 'title': '材料の追加'})

def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, '材料が正常に更新されました。')
            return redirect('inventory:material_detail', pk=material.pk)
    else:
        form = MaterialForm(instance=material)
    return render(request, 'inventory/material_form.html', {'form': form, 'material': material, 'title': '材料の編集'})

def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, '材料が削除されました。')
        return redirect('inventory:material_list')
    return render(request, 'inventory/material_confirm_delete.html', {'material': material})

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