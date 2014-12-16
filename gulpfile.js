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
    'js': [paths.js + '*.js', paths.js + '**/*.js', '!' + paths.js + '*.min.js', '!' + paths.js + '**/*.min.js']
};

// TASKS
//##########################################################
// TASKS/linting
gulp.task('lint', function () {
    gulp.src(patterns.js.concat(['!' + paths.js + 'libs/*.js', './gulpfile.js']))
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
