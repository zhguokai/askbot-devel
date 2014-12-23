// IMPORTS
//##########################################################
'use strict';

/* global require */
var gulp = require('gulp');
var gutil = require('gulp-util');
var jshint = require('gulp-jshint');
var jscs = require('gulp-jscs');
var closureCompiler = require('gulp-closure-compiler');

// SETTINGS
//##########################################################
var paths = {
    'media': 'askbot/media/',
    'js': 'askbot/media/js/',
    'dist': 'askbot/media/dist/'
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
        'bower_components/**/*.js',
        'node_modules/**/*.js',
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
        .pipe(jscs()).on('error', function (error) {
            gutil.log('\n' + error.message);
        })
        .pipe(jshint())
        .pipe(jshint.reporter('jshint-stylish'));
});

// TASKS/compiling
gulp.task('compile', function () {
    // gulp.src(patterns.js)
    gulp.src(patterns.js.concat(ignore.js.map(function (f) { return '!' + f; })))
        .pipe(closureCompiler({
            compilerPath: 'bower_components/closure-compiler/compiler.jar',
            fileName: 'build.js',
            compilerFlags: {
                externs: [
                    // 'askbot/media/js/libs',
                    // 'askbot/media/js/plugins',
                    // 'askbot/media/js/output-words.js',
                    // 'askbot/media/js/jquery.form.js',
                    // 'askbot/media/js/jquery.ajaxfileupload.js',
                    // 'askbot/media/js/jquery.history.js'
                ],
                jscomp_off: 'internetExplorerChecks'
            }
        }))
        .pipe(gulp.dest(paths.dist));
});

// // TASK/watchers
gulp.task('watch', function () {
    gulp.watch(patterns.js.concat(['./gulpfile.js']), ['lint']);
});

// RUNNERS
//##########################################################
gulp.task('default', ['lint', 'compile']);
