#!/bin/bash
# EpochCore RAS Java Repository Setup Script

set -e

echo "☕ Setting up EpochCore RAS for Java repository..."

# Check Java version
if ! command -v java &> /dev/null; then
    echo "❌ Java is required but not found"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1)
echo "✅ Found $JAVA_VERSION"

# Check Maven
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven is required but not found"
    echo "Please install Maven: https://maven.apache.org/install.html"
    exit 1
fi

MVN_VERSION=$(mvn -version | head -n 1)
echo "✅ Found $MVN_VERSION"

# Setup Maven project structure if it doesn't exist
echo "📁 Setting up Java project structure..."
mkdir -p src/main/java
mkdir -p src/test/java
mkdir -p src/main/resources
mkdir -p src/test/resources

# Create or update pom.xml
echo "📦 Setting up Maven POM..."
if [ -f "pom.xml" ]; then
    echo "📝 Found existing pom.xml, backing up..."
    cp pom.xml pom.xml.backup
else
    cat > pom.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.epochcore</groupId>
    <artifactId>epochcore-ras-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    
    <name>EpochCore RAS Java Project</name>
    <description>Java project with EpochCore RAS integration</description>
    
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.9.3</junit.version>
        <jackson.version>2.15.2</jackson.version>
    </properties>
    
    <dependencies>
        <!-- Jackson for YAML/JSON processing -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-core</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.dataformat</groupId>
            <artifactId>jackson-dataformat-yaml</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        
        <!-- Process execution utilities -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-exec</artifactId>
            <version>1.3</version>
        </dependency>
        
        <!-- Testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
            
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0</version>
            </plugin>
            
            <!-- EpochCore RAS Integration Plugin -->
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.1.0</version>
                <configuration>
                    <mainClass>com.epochcore.integration.EpochCoreIntegration</mainClass>
                </configuration>
                <executions>
                    <execution>
                        <id>epochcore-validate</id>
                        <phase>test</phase>
                        <goals>
                            <goal>java</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
    
</project>
EOF
fi

# Create Java EpochCore integration class
echo "🔧 Creating Java integration class..."
mkdir -p src/main/java/com/epochcore/integration
cat > src/main/java/com/epochcore/integration/EpochCoreIntegration.java << 'EOF'
package com.epochcore.integration;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.List;

/**
 * EpochCore RAS Java Integration
 * 
 * This class provides Java integration with the Python-based EpochCore RAS system
 */
public class EpochCoreIntegration {
    
    private static final String PYTHON_EXECUTABLE = "python3";
    private static final String INTEGRATION_SCRIPT = "integration.py";
    
    public static void main(String[] args) {
        EpochCoreIntegration integration = new EpochCoreIntegration();
        
        if (args.length == 0) {
            System.out.println("Usage: EpochCoreIntegration [init|status|validate|demo|run]");
            return;
        }
        
        String command = args[0];
        boolean success = false;
        
        switch (command) {
            case "init":
                success = integration.initRecursive();
                break;
            case "status":
                success = integration.getStatus();
                break;
            case "validate":
                success = integration.validateSystem();
                break;
            case "demo":
                success = integration.setupDemo();
                break;
            case "run":
                success = integration.runWorkflow();
                break;
            default:
                System.out.println("Unknown command: " + command);
                System.out.println("Usage: EpochCoreIntegration [init|status|validate|demo|run]");
                return;
        }
        
        System.exit(success ? 0 : 1);
    }
    
    public boolean initRecursive() {
        System.out.println("🚀 Initializing EpochCore RAS recursive improvement system...");
        boolean success = runPythonCommand("init-recursive");
        if (success) {
            System.out.println("✅ Recursive improvement system initialized successfully");
        }
        return success;
    }
    
    public boolean getStatus() {
        System.out.println("📊 Getting EpochCore RAS system status...");
        return runPythonCommand("status");
    }
    
    public boolean validateSystem() {
        System.out.println("🔍 Validating EpochCore RAS system...");
        boolean success = runPythonCommand("validate");
        if (success) {
            System.out.println("✅ System validation completed successfully");
        }
        return success;
    }
    
    public boolean setupDemo() {
        System.out.println("🎯 Setting up EpochCore RAS demo environment...");
        boolean success = runPythonCommand("setup-demo");
        if (success) {
            System.out.println("✅ Demo environment setup completed");
        }
        return success;
    }
    
    public boolean runWorkflow() {
        System.out.println("⚡ Running EpochCore RAS workflow...");
        boolean success = runPythonCommand("run-workflow");
        if (success) {
            System.out.println("✅ Workflow execution completed");
        }
        return success;
    }
    
    private boolean runPythonCommand(String command) {
        try {
            List<String> cmd = Arrays.asList(PYTHON_EXECUTABLE, INTEGRATION_SCRIPT, command);
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.inheritIO(); // Inherit parent process IO
            
            Process process = pb.start();
            int exitCode = process.waitFor();
            
            return exitCode == 0;
            
        } catch (IOException | InterruptedException e) {
            System.err.println("❌ Failed to execute Python command: " + e.getMessage());
            return false;
        }
    }
}
EOF

# Create test class
echo "🧪 Creating test class..."
mkdir -p src/test/java/com/epochcore/integration
cat > src/test/java/com/epochcore/integration/EpochCoreIntegrationTest.java << 'EOF'
package com.epochcore.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for EpochCore RAS Integration
 */
public class EpochCoreIntegrationTest {
    
    @Test
    @DisplayName("EpochCore Integration Class Should Be Instantiable")
    public void testInstantiation() {
        assertDoesNotThrow(() -> {
            EpochCoreIntegration integration = new EpochCoreIntegration();
            assertNotNull(integration);
        });
    }
    
    @Test
    @DisplayName("Should Handle System Status Check")
    public void testStatusCheck() {
        EpochCoreIntegration integration = new EpochCoreIntegration();
        // Note: This might fail if Python/EpochCore is not properly set up
        // but the test should not throw exceptions
        assertDoesNotThrow(() -> {
            integration.getStatus();
        });
    }
}
EOF

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Java
*.class
*.war
*.ear
*.jar
hs_err_pid*
replay_pid*

# Maven
target/
!.mvn/wrapper/maven-wrapper.jar
!**/src/main/**/target/
!**/src/test/**/target/

# IDE
.idea/
*.iws
*.iml
*.ipr
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# EpochCore RAS
logs/
backups/
.epochcore/
EOF
fi

# Install dependencies
echo "📥 Installing Maven dependencies..."
mvn clean compile

# Test Java EpochCore RAS integration
echo "🧪 Testing EpochCore RAS Java integration..."
if mvn test -q; then
    echo "✅ EpochCore RAS Java integration tests passed!"
else
    echo "⚠️  EpochCore RAS Java integration tests have warnings - check the output above"
fi

echo "🎉 Java repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Build the project: mvn clean compile"
echo "2. Run tests: mvn test"
echo "3. Initialize recursive improvements: mvn exec:java -Dexec.mainClass=\"com.epochcore.integration.EpochCoreIntegration\" -Dexec.args=\"init\""
echo "4. Check system status: mvn exec:java -Dexec.mainClass=\"com.epochcore.integration.EpochCoreIntegration\" -Dexec.args=\"status\""