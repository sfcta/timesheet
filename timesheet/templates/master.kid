<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import sitetemplate,cherrypy
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <script src="/static/MochiKit.js"></script>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <meta py:replace="item[:]" name="description" content="master template"/>
    <style type="text/css" media="screen">
        #pageLogin
        {
            font-size: 10px;
            font-family: verdana;
            text-align: right;
        }
    </style>

    <link rel="stylesheet" type="text/css" media="screen" href="../static/css/styles.css"
          py:attrs="href=tg.url('/static/css/styles.css')"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">

    <div py:if="tg.config('identity.on') and not defined('logging_in')" id="pageLogin">
        <span py:if="tg.identity.anonymous">
            <a href="${tg.url('/login')}">Login</a>
        </span>
        <span py:if="not tg.identity.anonymous">
            &nbsp;
        </span>
    </div>

    <div id="header">&#160;</div>
    <div id="headerlink"><a href="http://http://codingforums.com/"></a></div>

    <div id="main_content">

        <!-- flash and warning boxes -->
        <span py:if="tg_flash != None and tg_flash[0] != '!'">
          <div id="status_block" class="flash" py:if="value_of('tg_flash',None)" py:content="tg_flash"></div>
        </span>
        <span py:if="tg_flash != None and tg_flash[0] == '!'">
          <div id="warning_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash[1:]"></div>
        </span>

        <!-- main content -->
        <div py:replace="[item.text]+item[:]">page content</div>
    </div>

    <div id="footer">
        <p>(c) 2009 San Francisco County Transportion Authority</p>
    </div>
</body>

</html>
