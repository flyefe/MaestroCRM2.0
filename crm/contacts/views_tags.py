from django.shortcuts import render, redirect, get_object_or_404
from .models import Tag
from .forms import TagForm

from django.contrib.auth.decorators import login_required
from core.decorators import role_required

# View to create a new Tag
@login_required
def tag_list(request):
    tags = Tag.objects.all()  # Fetch all tags for display

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('tag_list')  # Redirect to tag list view
    else:
        form = TagForm()  # Provide an empty form for GET requests

    # Render the form and tags
    return render(request, 'tags/tag_list.html', {
        'form': form,
        'tags': tags
    })


# View to update an existing Tag
@role_required(['Admin'])
@login_required
def edit_tag(request, tag_id):
    # Fetch the tag object or return a 404 if not found
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)  # Bind form to the existing tag
        if form.is_valid():
            form.save()  # Save the updates to the database
            return redirect('tag_list')  # Redirect to tag list view
    else:
        form = TagForm(instance=tag)  # Prepopulate form with current tag data

    # Render the form for updating
    return render(request, 'tags/edit_tags.html', {
        'form': form,
        'is_update': True,  # Optional flag to indicate update mode in the template
        'tag': tag
    })

# View to delete an existing Tag
@role_required(['Admin'])
@login_required
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)  # Fetch tag object

    if request.method == 'POST':
        tag.delete()  # Delete the tag from the database
        return redirect('tag_list')  # Redirect to tag list view

    # Confirm deletion with a simple template
    return render(request, 'tag_confirm_delete.html', {
        'tag': tag
    })
