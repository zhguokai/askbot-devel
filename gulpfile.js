// IMPORTS
//##########################################################
'use strict';

/* global require */
var gulp = require('gulp');
var gutil = require('gulp-util');
var jshint = require('gulp-jshint');
var jscs = require('gulp-jscs');

// SETTINGS
//##########################################################
var paths = {
    'js': './askbot/media/js/'
};

var patterns = {
    'js': [
        paths.js + '*.js',
        paths.js + '**/*.js'
    ]
};

var ignore = {
    'js': [
        './gulpfile.js',
        paths.js + '*.min.js',
        paths.js + '**/*.min.js',
        paths.js + 'libs/*.js',
        paths.js + 'plugins/*.js',
        paths.js + 'plugins/**/*.js',
        // these look like they are not used anywhere but we keep em for now
        paths.js + 'output-words.js',
        paths.js + 'jquery.form.js',
        paths.js + 'jquery.ajaxfileupload.js',
        paths.js + 'jquery.history.js'
    ]
};

// TASKS
//##########################################################
// TASKS/linting
gulp.task('lint', function () {
    gulp.src(patterns.js.concat(ignore.js.map(function (f) { return '!' + f; })))
        .pipe(jshint())
        .pipe(jshint.reporter('jshint-stylish'))
        .pipe(jscs()).on('error', function (error) {
            gutil.log('\n' + error.message);
        });
});

// // TASK/watchers
gulp.task('watch', function () {
    gulp.watch(patterns.js.concat(['./gulpfile.js']), ['lint']);
});

// RUNNERS
//##########################################################
gulp.task('default', ['lint']);
