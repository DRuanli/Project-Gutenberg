# ---- webapp/routes.py ----

import os
import uuid
import json
import re
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from webapp.forms import GutenbergIdForm, FileUploadForm, AnalysisOptionsForm, ComparisonForm
from webapp.utils import (
    download_gutenberg_books, 
    analyze_book, 
    generate_visualizations,
    analyze_themes,
    compare_books,
    get_available_books
)

main = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/', methods=['GET', 'POST'])
def index():
    """Home page with forms for book ID input and file upload"""
    gutenberg_form = GutenbergIdForm()
    upload_form = FileUploadForm()
    
    if gutenberg_form.validate_on_submit():
        # Process Gutenberg book IDs
        # Handle both comma and space-separated IDs
        book_id_input = gutenberg_form.book_ids.data
        book_ids = [int(id.strip()) for id in re.split(r'[,\s]+', book_id_input) if id.strip()]
        session_id = str(uuid.uuid4())
        book_paths = download_gutenberg_books(book_ids, session_id)
        
        if book_paths:
            return redirect(url_for('main.analyze', session_id=session_id))
        else:
            flash('Failed to download books. Please try again.', 'danger')
    
    if upload_form.validate_on_submit():
        # Process uploaded file
        if upload_form.file.data and allowed_file(upload_form.file.data.filename):
            session_id = str(uuid.uuid4())
            os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], session_id), exist_ok=True)
            
            filename = secure_filename(upload_form.file.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id, filename)
            upload_form.file.data.save(file_path)
            
            return redirect(url_for('main.analyze', session_id=session_id))
        else:
            flash('Invalid file. Please upload a text file.', 'danger')
    
    # Provide option to analyze existing books
    available_books = get_available_books()
    
    return render_template('index.html', 
                          gutenberg_form=gutenberg_form, 
                          upload_form=upload_form,
                          available_books=available_books)

@main.route('/analyze/<session_id>', methods=['GET', 'POST'])
def analyze(session_id):
    """Page for configuring analysis options"""
    options_form = AnalysisOptionsForm()
    
    if options_form.validate_on_submit():
        # Save analysis options
        options = {
            'remove_stopwords': options_form.remove_stopwords.data,
            'lemmatize': options_form.lemmatize.data,
            'top_words': options_form.top_words.data,
            'generate_wordcloud': options_form.generate_wordcloud.data,
            'generate_charts': options_form.generate_charts.data,
            'analyze_themes': options_form.analyze_themes.data,
            'num_topics': options_form.num_topics.data
        }
        
        # Save options to session file
        options_path = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id, 'options.json')
        with open(options_path, 'w') as f:
            json.dump(options, f)
        
        # Run analysis with selected options
        success = analyze_book(session_id, options)
        
        if success:
            return redirect(url_for('main.results', session_id=session_id))
        else:
            flash('Analysis failed. Please try again.', 'danger')
    
    # Get the book files for this session
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
    book_files = [f for f in os.listdir(upload_dir) if f.endswith('.txt')]
    
    return render_template('analyze.html', 
                          form=options_form, 
                          session_id=session_id,
                          book_files=book_files)

@main.route('/results/<session_id>')
def results(session_id):
    """Page displaying analysis results"""
    results_dir = os.path.join(current_app.config['RESULTS_FOLDER'], session_id)
    
    # Check if results exist
    if not os.path.exists(results_dir):
        flash('Results not found. Please run the analysis first.', 'warning')
        return redirect(url_for('main.index'))
    
    # Load analysis results
    with open(os.path.join(results_dir, 'summary.json'), 'r') as f:
        summary = json.load(f)
    
    # Get paths to visualization files
    visualizations = []
    viz_dir = os.path.join(results_dir, 'visualizations')
    if os.path.exists(viz_dir):
        for viz_file in os.listdir(viz_dir):
            if viz_file.endswith('.png'):
                visualizations.append(viz_file)
    
    # Load top words data
    with open(os.path.join(results_dir, 'top_words.json'), 'r') as f:
        top_words = json.load(f)
    
    return render_template('results.html',
                          session_id=session_id,
                          summary=summary,
                          visualizations=visualizations,
                          top_words=top_words)

@main.route('/visualizations/<session_id>/<filename>')
def visualization(session_id, filename):
    """Serve visualization files"""
    return send_from_directory(os.path.join(current_app.config['RESULTS_FOLDER'], 
                                           session_id, 'visualizations'), 
                              filename)

@main.route('/compare/<session_id>', methods=['GET', 'POST'])
def compare(session_id):
    """Page for comparing two books"""
    results_dir = os.path.join(current_app.config['RESULTS_FOLDER'], session_id)
    
    # Get available books for this session
    available_books = []
    if os.path.exists(results_dir):
        with open(os.path.join(results_dir, 'summary.json'), 'r') as f:
            summary = json.load(f)
            available_books = [(book['id'], book['title']) for book in summary['books']]
    
    if len(available_books) < 2:
        flash('Need at least two books for comparison.', 'warning')
        return redirect(url_for('main.results', session_id=session_id))
    
    # Create form with dynamic choices
    form = ComparisonForm()
    form.book1.choices = available_books
    form.book2.choices = available_books
    
    if form.validate_on_submit() and form.book1.data != form.book2.data:
        # Run comparison
        success = compare_books(session_id, form.book1.data, form.book2.data)
        
        if success:
            return redirect(url_for('main.comparison_results', 
                                   session_id=session_id,
                                   book1=form.book1.data,
                                   book2=form.book2.data))
        else:
            flash('Comparison failed. Please try again.', 'danger')
    
    return render_template('compare.html', form=form, session_id=session_id)

@main.route('/comparison_results/<session_id>/<book1>/<book2>')
def comparison_results(session_id, book1, book2):
    """Page displaying comparison results between two books"""
    # Get comparison results
    comparison_path = os.path.join(current_app.config['RESULTS_FOLDER'], 
                                  session_id, 'comparisons', f'{book1}_vs_{book2}.json')
    
    if not os.path.exists(comparison_path):
        flash('Comparison results not found.', 'warning')
        return redirect(url_for('main.compare', session_id=session_id))
    
    with open(comparison_path, 'r') as f:
        comparison_data = json.load(f)
    
    # Get visualization paths
    viz_dir = os.path.join(current_app.config['RESULTS_FOLDER'], 
                          session_id, 'comparisons', 'visualizations')
    viz_file = f'{book1}_vs_{book2}_comparison.png'
    wordcloud_file = f'{book1}_vs_{book2}_wordcloud.png'
    
    return render_template('comparison_results.html',
                          session_id=session_id,
                          book1=book1,
                          book2=book2,
                          comparison=comparison_data,
                          viz_file=viz_file if os.path.exists(os.path.join(viz_dir, viz_file)) else None,
                          wordcloud_file=wordcloud_file if os.path.exists(os.path.join(viz_dir, wordcloud_file)) else None)

@main.route('/themes/<session_id>')
def themes(session_id):
    """Page displaying theme analysis results"""
    themes_path = os.path.join(current_app.config['RESULTS_FOLDER'], 
                              session_id, 'themes', 'themes.json')
    
    if not os.path.exists(themes_path):
        # Run theme analysis if not already done
        with open(os.path.join(current_app.config['RESULTS_FOLDER'], session_id, 'summary.json'), 'r') as f:
            summary = json.load(f)
        
        if len(summary['books']) < 2:
            flash('Need at least two books for theme analysis.', 'warning')
            return redirect(url_for('main.results', session_id=session_id))
        
        success = analyze_themes(session_id)
        
        if not success:
            flash('Theme analysis failed. Please try again.', 'danger')
            return redirect(url_for('main.results', session_id=session_id))
    
    # Load theme analysis results
    with open(themes_path, 'r') as f:
        themes_data = json.load(f)
    
    return render_template('themes.html',
                          session_id=session_id,
                          themes=themes_data)
