import os
from django.shortcuts import render, redirect
from . import util
import markdown
import random
from django import forms


ENTRIES_DIR = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'entries')


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry_content = util.get_entry(title)  # Get the entry content
    if entry_content:
        html_content = markdown.markdown(
            entry_content)  # Convert Markdown to HTML
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content  # Use the converted HTML content
        })
    else:
        # Render the error template with a message
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })


def random_entry(request):
    entries = util.list_entries()  # Get the list of all entries
    if entries:
        random_entry = random.choice(entries)  # Choose a random entry
        # Redirect to the random entry page
        return redirect('entry', title=random_entry)
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries found."
        })


# Define a form class to create a new entry
class NewEntryForm(forms.Form):
    title = forms.CharField(
        label="Title",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        label="Content",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3})
    )


def create_new_entry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if an entry with the same title already exists
            if util.get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "message": "An entry with this title already exists."
                })

            # Save the new entry using the util.save_entry() function
            util.save_entry(title, content)

            # Redirect to the newly created entry page
            return redirect('entry', title=title)

    else:
        form = NewEntryForm()

    return render(request, "encyclopedia/create.html", {
        "form": form
    })


class EditEntryForm(forms.Form):
    content = forms.CharField(
        label="Content",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10
        })
    )


def edit_entry(request, title):
    # Get the current content of the entry
    current_content = util.get_entry(title)

    if current_content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })

    # Handle form submission
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            # Save the updated content
            util.save_entry(title, form.cleaned_data["content"])
            return redirect('entry', title=title)

    # If GET request, pre-populate form with current content
    form = EditEntryForm(initial={'content': current_content})
    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title
    })


def delete_entry(request, title):
    if request.method == "POST":
        # Check if the entry exists
        entry_content = util.get_entry(title)
        if entry_content is None:
            return render(request, "encyclopedia/error.html", {
                "message": "The requested page was not found."
            })

        # Delete the entry
        util.delete_entry(title)
        return redirect('index')  # Redirect to the homepage after deletion

    # If not POST, just redirect to the entry page
    return redirect('entry', title=title)


def search(request):
    query = request.GET.get('q', '').strip()  # Get the search query
    entries = util.list_entries()  # Get all entries

    if query:  # If there's a query
        # Check if an exact match exists
        if query in entries:
            return redirect('entry', title=query)  # Redirect to the entry page

        # Check for partial matches (case-insensitive)
        matching_entries = [
            entry for entry in entries if query.lower() in entry.lower()]

        if matching_entries:
            return render(request, "encyclopedia/search_results.html", {
                "query": query,
                "entries": matching_entries
            })
        else:
            # If no matches are found, show the error page
            return render(request, "encyclopedia/error.html", {
                "message": f'No encyclopedia entry found for "{query}".'
            })
    else:
        # If query is empty, return to the index page
        return redirect('index')
